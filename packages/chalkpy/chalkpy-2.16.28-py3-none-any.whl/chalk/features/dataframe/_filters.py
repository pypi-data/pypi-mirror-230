from __future__ import annotations

import collections.abc
import datetime
import enum
import functools
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Mapping, Optional, Sequence, Type, TypeVar, Union

from chalk.features import FeatureConverter
from chalk.features.feature_field import Feature
from chalk.features.feature_wrapper import FeatureWrapper, unwrap_feature
from chalk.features.filter import Filter, TimeDelta, _get_filter_now
from chalk.utils.collections import ensure_tuple

if TYPE_CHECKING:
    import polars as pl
    import pyarrow as pa
    import pyarrow.compute as pc

DType = TypeVar("DType", "pl.PolarsDataType", "pa.lib.DataType")
ParsedExpr = TypeVar("ParsedExpr", "pl.Expr", "pa.compute.Expression")


class FilterConverter(Generic[DType, ParsedExpr]):
    """
    Converts a Filter expression tree into a polars or pyarrow expression
    that can be used to filter tables of the corresponding type.
    """

    def _expr_type(self) -> Type[ParsedExpr]:
        """Need this for isinstance() checks, TypeVar is insufficient :-("""
        raise NotImplementedError()

    def _is_expr(self, o: Any) -> bool:
        return isinstance(o, self._expr_type())

    def _expr_column(self, name: str) -> ParsedExpr:
        """Expression for selecting a column by the given name"""
        raise NotImplementedError()

    def _expr_literal(self, value: Any, dtype: Optional[DType] = None) -> ParsedExpr:
        """Expression for a literal value"""
        raise NotImplementedError()

    def _expr_is_null(self, expr: ParsedExpr) -> ParsedExpr:
        """Expression for checking null"""
        raise NotImplementedError()

    def _expr_is_not_null(self, expr: ParsedExpr) -> ParsedExpr:
        """Should be equivalent to `not _expr_is_null(expr)`."""
        raise NotImplementedError()

    def _expr_is_in_sequence_lit(self, expr: ParsedExpr, values: Sequence, dtype: DType) -> ParsedExpr:
        """
        Returns an expression that checks whether `expr` is in a sequence of literal values.
        i.e. analogous to `lambda x: expr(x) in values`
        """
        raise NotImplementedError()

    def _expr_is_eq_lit(self, expr: ParsedExpr, value: Any, dtype: DType) -> ParsedExpr:
        """
        Compares an expression to a literal value.
        i.e. analogous to `lambda x: expr(x) == value`
        """
        return expr == self._expr_literal(value, dtype=dtype)

    def _expr_is_in(self, lhs: ParsedExpr, rhs: Sequence, lhs_dtype: DType):
        """Filter for where the lhs is in the RHS. The RHS must be a literal collection."""
        if self._dtype_is_struct(lhs_dtype):
            lhs_adapter: StructAdapter[DType] = StructAdapter.from_raw(lhs_dtype)
            # Assert equality field by field
            filters = []
            rhs_by_fields: Dict[str, List[Any]] = collections.defaultdict(list)
            for item in rhs:
                for field in lhs_adapter.fields():
                    # Assuming that struct-like objects make their members accessible by attribute name or __getitem__
                    try:
                        rhs_vector = getattr(item, field.name)
                    except AttributeError:
                        rhs_vector = item[field.name]
                    rhs_by_fields[field.name].append(rhs_vector)
            for field in lhs_adapter.fields():
                field_name = field.name
                new_lhs = lhs_adapter.get_field_by_name(lhs, field_name)
                new_lhs_dtype = field.dtype
                new_rhs = rhs_by_fields[field_name]
                filters.append(self._expr_is_in(new_lhs, new_rhs, new_lhs_dtype))
            assert len(filters) > 0, "structs with 0 fields are unsupported"
            return functools.reduce(lambda a, b: a & b, filters)
        return self._expr_is_in_sequence_lit(expr=lhs, values=rhs, dtype=lhs_dtype)

    def _expr_is_eq(
        self,
        lhs: Any,
        rhs: Any,
        lhs_dtype: Optional[DType],
        rhs_dtype: Optional[DType],
    ):
        if rhs_dtype is not None:
            if lhs_dtype is None:
                # Swap the columns
                return self._expr_is_eq(rhs, lhs, rhs_dtype, lhs_dtype)
            else:
                # Comparing two columns
                assert self._is_expr(lhs)
                assert self._is_expr(rhs)
                if self._dtype_is_struct(lhs_dtype):
                    assert self._dtype_is_struct(rhs_dtype)
                    # Assert equality field by field
                    filters = []
                    lhs_adapter: StructAdapter[DType] = StructAdapter.from_raw(lhs_dtype)
                    rhs_adapter: StructAdapter[DType] = StructAdapter.from_raw(rhs_dtype)
                    for field in lhs_adapter.fields():
                        field_name = field.name
                        new_lhs = lhs_adapter.get_field_by_name(lhs, field_name)
                        new_lhs_dtype = field.dtype
                        new_rhs = rhs_adapter.get_field_by_name(rhs, field_name)
                        new_rhs_dtype = field.dtype
                        filters.append(self._expr_is_eq(new_lhs, new_rhs, new_lhs_dtype, new_rhs_dtype))
                    assert len(filters) > 0, "structs with 0 fields are unsupported"
                    return functools.reduce(lambda a, b: a & b, filters)
                return lhs == rhs
        # rhs is literal
        # lhs is a column
        assert lhs_dtype is not None, "one side must be a column"
        assert self._is_expr(lhs)
        if self._dtype_is_struct(lhs_dtype):
            # Assert equality field by field
            filters = []
            lhs_adapter = StructAdapter.from_raw(lhs_dtype)
            for field in lhs_adapter.fields():
                field_name = field.name
                new_lhs = lhs_adapter.get_field_by_name(lhs, field_name)
                new_lhs_dtype = field.dtype
                # Assuming that struct-like objects make their members accessible by attribute name or __getitem__
                try:
                    new_rhs = getattr(rhs, field_name)
                except AttributeError:
                    new_rhs = rhs[field_name]
                new_rhs_dtype = None  # literal values do not have dtypes
                filters.append(self._expr_is_eq(new_lhs, new_rhs, new_lhs_dtype, new_rhs_dtype))
            assert len(filters) > 0, "structs with 0 fields are unsupported"
            return functools.reduce(lambda a, b: a & b, filters)
        return self._expr_is_eq_lit(lhs, rhs, lhs_dtype)

    def _feature_converter_dtype(self, converter: FeatureConverter) -> DType:
        raise NotImplementedError()

    def _dtype_type(self) -> Type[DType]:
        raise NotImplementedError()

    def _dtype_is_struct(self, dtype: DType) -> bool:
        raise NotImplementedError()

    def convert_filters(
        self,
        filters: Sequence[Filter],
        df_schema: Mapping[str, DType],
        timestamp_feature: Optional[Feature] = None,
        now: Optional[datetime.datetime] = None,
        now_col_name: Optional[str] = None,
    ) -> Optional[ParsedExpr]:
        if len(filters) == 0:
            return None
        parsed_filters = (
            self._convert_filter_to_expr(f, df_schema, timestamp_feature, now, now_col_name) for f in filters
        )
        return functools.reduce(lambda a, b: a & b, parsed_filters)

    def _convert_filter_to_expr(
        self,
        f: Filter,
        df_schema: Mapping[str, DType],
        timestamp_feature: Optional[Feature] = None,
        now: Optional[datetime.datetime] = None,
        now_col_name: Optional[str] = None,
    ) -> ParsedExpr:

        # Passing `now` in explicitly instead of using datetime.datetime.now() so that multiple filters
        # relying on relative timestamps (e.g. before, after) will have the same "now" time.
        def _convert_sub_filter(sub_filter: Filter, side_name: str):
            assert isinstance(sub_filter, Filter), f"{side_name} must be a filter"
            return self._convert_filter_to_expr(sub_filter, df_schema, timestamp_feature, now, now_col_name)

        if f.operation == "not":
            assert f.rhs is None, "not has just one side"
            return ~_convert_sub_filter(f.lhs, "lhs")
        elif f.operation == "and":
            return _convert_sub_filter(f.lhs, "lhs") & _convert_sub_filter(f.rhs, "rhs")
        elif f.operation == "or":
            return _convert_sub_filter(f.lhs, "lhs") | _convert_sub_filter(f.rhs, "rhs")

        lhs = self._parse_feature_or_value(f.lhs, timestamp_feature, now, now_col_name)
        rhs = self._parse_feature_or_value(f.rhs, timestamp_feature, now, now_col_name)

        lhs_converter = None
        if isinstance(lhs, Feature):
            lhs_converter = lhs.converter
            col_name = str(lhs)
            if col_name not in df_schema:
                raise KeyError(f"Feature {col_name} not in DataFrame with columns [{', '.join(df_schema.keys())}]")
            lhs = self._expr_column(col_name)

        rhs_converter = None
        if isinstance(rhs, Feature):
            rhs_converter = rhs.converter
            col_name = str(rhs)
            if col_name not in df_schema:
                raise KeyError(f"Feature {col_name} not in DataFrame with columns [{', '.join(df_schema.keys())}]")
            rhs = self._expr_column(col_name)

        # if not (self._is_expr(lhs) or self._is_expr(rhs)):
        if lhs_converter is None:
            # LHS is literal. Encode it into the rhs_dtype
            if rhs_converter is not None and not self._is_expr(lhs):
                lhs = rhs_converter.from_rich_to_primitive(lhs)
        if rhs_converter is None and not self._is_expr(rhs):
            # RHS is literal. Encode it into the lhs_dtype
            if lhs_converter is not None and not self._is_expr(rhs):
                if f.operation in ("in", "not in"):
                    assert isinstance(rhs, collections.abc.Iterable)
                    rhs = [lhs_converter.from_rich_to_primitive(x) for x in rhs]
                else:
                    rhs = lhs_converter.from_rich_to_primitive(rhs)

        if rhs is None:
            assert self._is_expr(lhs)
            if f.operation == "==":
                return self._expr_is_null(lhs)

            elif f.operation == "!=":
                return self._expr_is_not_null(lhs)

        if f.operation in ("in", "not in"):
            assert lhs_converter is not None
            assert self._is_expr(lhs)
            assert isinstance(rhs, collections.abc.Iterable)
            ret = self._expr_is_in(lhs, rhs, self._feature_converter_dtype(converter=lhs_converter))
            if f.operation == "not in":
                ret = ~ret
        elif f.operation in ("==", "!="):
            ret = self._expr_is_eq(
                lhs=lhs,
                rhs=rhs,
                lhs_dtype=lhs_converter and self._feature_converter_dtype(lhs_converter),
                rhs_dtype=rhs_converter and self._feature_converter_dtype(rhs_converter),
            )
            if f.operation == "!=":
                ret = ~ret
        elif f.operation == "!=":
            ret = lhs != rhs
        elif f.operation == ">=":
            ret = lhs >= rhs
        elif f.operation == ">":
            ret = lhs > rhs
        elif f.operation == "<":
            ret = lhs < rhs
        elif f.operation == "<=":
            ret = lhs <= rhs
        else:
            raise ValueError(f'Unknown operation "{f.operation}"')
        assert self._is_expr(ret)
        return ret

    def _parse_feature_or_value(
        self,
        f: Union[Feature, Any],
        timestamp_feature: Optional[Feature],
        now: Optional[datetime.datetime],
        now_column_name: Optional[str],
    ):
        """Parse a feature or value into the correct type that can be used for filtering."""
        f = self._feature_type_or_value(f)
        f = self._maybe_convert_timedelta_to_timestamp(f, now, now_column_name)
        f = self._maybe_replace_timestamp_feature(f, timestamp_feature)
        if isinstance(f, enum.Enum):
            f = f.value
        return f

    def _feature_type_or_value(self, e: Union[Feature, FeatureWrapper, Any]) -> Union[Feature, Any]:
        if isinstance(e, FeatureWrapper):
            e = unwrap_feature(e)
        return e

    def _maybe_convert_timedelta_to_timestamp(
        self,
        f: Union[TimeDelta, datetime.timedelta, Any],
        now: Optional[datetime.datetime],
        now_column_name: Optional[str] = None,
    ) -> Union[ParsedExpr, datetime.datetime, Any]:
        """Convert timedeltas relative to ``now`` into absolute datetimes."""
        if now and now_column_name is not None:
            raise ValueError(
                "Can't specify both now and now_column_name -- one or the other must be used as a point of reference for "
                "the time delta"
            )
        if isinstance(f, TimeDelta):
            f = f.to_std()
        if isinstance(f, datetime.timedelta):
            if now is None and now_column_name is None:
                raise ValueError(
                    "The filter contains a relative timestamp. The current datetime or current date column "
                    "must be provided to evaluate this filter."
                )
            if now_column_name:
                # creates a polars/pyarrow expression that evaluates to dates that are within the timedelta specified by `f`
                return self._expr_column(now_column_name) + self._expr_literal(f)
            return now + f

        return f

    def _maybe_replace_timestamp_feature(
        self, f: Union[Feature, Any], observed_at_feature: Optional[Feature]
    ) -> Feature:
        """Replace the ``CHALK_TS`` pseudo-feature with the actual timestamp column."""
        if not isinstance(f, Feature) or f.fqn != "__chalk__.CHALK_TS":
            return f
        if observed_at_feature is not None:
            return observed_at_feature
        raise ValueError("No Timestamp Feature Found")


class PolarsFilterConverter(FilterConverter["pl.PolarsDataType", "pl.Expr"]):
    def _dtype_type(self) -> Type[pl.DataType]:
        import polars as pl

        return pl.DataType

    def _dtype_is_struct(self, dtype: DType) -> bool:
        import polars as pl

        return dtype == pl.Struct

    def _expr_type(self) -> Type[pl.Expr]:
        import polars as pl

        return pl.Expr

    def _expr_column(self, name: str) -> pl.Expr:
        import polars as pl

        return pl.col(name)

    def _expr_literal(self, value: Any, dtype: Optional[pl.DataType] = None) -> pl.Expr:
        import polars as pl

        return pl.lit(value, dtype=dtype, allow_object=True)

    def _expr_is_null(self, expr: pl.Expr) -> pl.Expr:
        return expr.is_null()

    def _expr_is_not_null(self, expr: pl.Expr) -> pl.Expr:
        return expr.is_not_null()

    def _feature_converter_dtype(self, converter: FeatureConverter) -> pl.PolarsDataType:
        return converter.polars_dtype

    def _expr_is_in_sequence_lit(self, expr: pl.Expr, values: Sequence, dtype: pl.DataType):
        import polars as pl

        if not isinstance(dtype, type):
            dtype = type(dtype)
        return expr.is_in(pl.lit(pl.Series(values=values, dtype=dtype), allow_object=True))

    def _expr_is_eq_lit(self, expr: pl.Expr, value: Any, dtype: pl.DataType):
        import polars as pl

        if not isinstance(dtype, type):
            dtype = type(dtype)
        assert issubclass(dtype, pl.DataType)
        return expr == pl.lit(value, dtype=dtype, allow_object=True)


class PyArrowFilterConverter(FilterConverter["pa.lib.DataType", "pa.compute.Expression"]):
    def _dtype_type(self) -> Type[pa.lib.DataType]:
        import pyarrow as pa

        return pa.lib.DataType

    def _dtype_is_struct(self, dtype: pa.StructType) -> bool:
        import pyarrow as pa

        return pa.types.is_struct(dtype)

    def _expr_type(self) -> Type[pa.compute.Expression]:
        import pyarrow as pa

        return pa.compute.Expression

    def _expr_column(self, name: str) -> pa.compute.Expression:
        import pyarrow as pa

        return pa.compute.field(name)

    def _expr_literal(self, value: Any, dtype: Optional[pa.DataType] = None) -> pa.compute.Expression:
        import pyarrow as pa

        return pa.compute.scalar(value)

    def _expr_is_null(self, expr: pa.compute.Expression) -> pa.compute.Expression:
        return expr.is_null()

    def _expr_is_not_null(self, expr: pa.compute.Expression) -> pa.compute.Expression:
        return ~expr.is_null()

    def _feature_converter_dtype(self, converter: FeatureConverter) -> pa.lib.DataType:
        return converter.pyarrow_dtype

    def _expr_is_in_sequence_lit(self, expr: pa.compute.Expression, values: Sequence, dtype: pa.DataType):
        import pyarrow as pa

        values = pa.compute.cast(values, target_type=dtype)
        return expr.isin(values)

    def _expr_is_eq_lit(self, expr: ParsedExpr, value: Any, dtype: DType) -> ParsedExpr:
        """
        Compares an expression to a literal value.
        i.e. analogous to `lambda x: expr(x) == value`
        """
        if value is None:
            return expr.is_null()
        return (~expr.is_null()) & (expr == self._expr_literal(value, dtype=dtype))


def convert_filters_to_pl_expr(
    filters: Sequence[Filter],
    df_schema: Mapping[str, pl.PolarsDataType],
    timestamp_feature: Optional[Feature] = None,
    now: Optional[datetime.datetime] = None,
    now_col_name: Optional[str] = None,
):
    return PolarsFilterConverter().convert_filters(filters, df_schema, timestamp_feature, now, now_col_name)


@dataclass
class StructField(Generic[DType]):
    name: str
    dtype: DType


class StructAdapter(Generic[DType, ParsedExpr]):
    """
    Wrapper for a polars or pyarrow struct.
    """

    def __init__(self, struct_type: DType):
        self._struct_type = struct_type

    def underlying(self) -> DType:
        return self._struct_type

    def fields(self):
        return [self._adapt_field(f) for f in self._raw_fields()]

    def get_field_by_name(self, expr: ParsedExpr, name: str) -> ParsedExpr:
        raise NotImplementedError()

    def _raw_fields(self):
        raise NotImplementedError()

    def _adapt_field(self, underlying_field) -> StructField[DType]:
        raise NotImplementedError()

    @staticmethod
    def from_polars(polars_dtype: pl.Struct) -> "StructAdapter[pl.Struct, pl.Expr]":
        return PolarsStructAdapter(polars_dtype)

    @staticmethod
    def from_pyarrow(pyarrow_dtype: pa.lib.StructType) -> "StructAdapter[pa.lib.StructType, pa.compute.Expression]":
        return PyArrowStructAdapter(pyarrow_dtype)

    @classmethod
    def from_raw(cls, raw_dtype: DType) -> "StructAdapter[DType, ParsedExpr]":
        import polars as pl
        import pyarrow as pa

        if isinstance(raw_dtype, pl.Struct):
            return cls.from_polars(raw_dtype)
        elif isinstance(raw_dtype, pa.StructType):
            return cls.from_pyarrow(raw_dtype)
        else:
            raise ValueError(f"Object {raw_dtype} is not a valid struct type.")


class PolarsStructAdapter(StructAdapter["pl.Struct", "pl.Expr"]):
    def _raw_fields(self) -> List[pl.Struct]:
        return list(self._struct_type.fields)

    def _adapt_field(self, underlying_field) -> StructField[pl.Struct]:
        return StructField(underlying_field.name, underlying_field.dtype)

    def get_field_by_name(self, expr: pl.Expr, name: str) -> pl.Expr:
        return expr.struct.field(name)


class PyArrowStructAdapter(StructAdapter["pa.StructType", "pa.compute.Expression"]):
    def __init__(self, struct_type: pa.StructType):
        super().__init__(struct_type)
        self._field_to_idx: Dict[str, idx] = {name: idx for idx, name in enumerate(f.name for f in struct_type)}
        pass

    def _raw_fields(self) -> List[pa.StructType]:
        return list(self._struct_type)

    def _adapt_field(self, underlying_field) -> StructField[pa.StructType]:
        return StructField(underlying_field.name, underlying_field.type)

    def get_field_by_name(self, expr: pa.compute.Expression, name: str) -> pa.compute.Expression:
        import pyarrow as pa
        import pyarrow.compute as pc

        idx = self._field_to_idx.get(name)
        if idx is None:
            raise ValueError(f"Unable to find field {name} in struct {self._struct_type}")
        return pa.compute.struct_field(expr, [idx])


def filter_data_frame(
    item: Any,
    underlying: Union[pl.DataFrame, pl.LazyFrame],
    namespace: Optional[str],
) -> Union[pl.DataFrame, pl.LazyFrame]:
    # Use the Chalk projection / selection syntax, where we support our Filter objects and
    # selection by column name
    from chalk.features.feature_set import FeatureSetBase

    projections: list[str] = []
    filters: List[Filter] = []
    for x in ensure_tuple(item):
        if isinstance(x, (FeatureWrapper, Feature, str)):
            projections.append(str(x))

        elif isinstance(x, Filter):
            filters.append(x)
        else:
            raise TypeError(
                "When indexing by Filters or Features, it is not simultaneously possible to perform other indexing operations."
            )
    now = _get_filter_now()
    # now = datetime.datetime.now(tz=datetime.timezone.utc)
    timestamp_feature = None if namespace is None else FeatureSetBase.registry[namespace].__chalk_ts__
    pl_expr = convert_filters_to_pl_expr(filters, underlying.schema, timestamp_feature, now)
    df = underlying
    if pl_expr is not None:
        df = df.filter(pl_expr)
    # Do the projection
    if len(projections) > 0:
        polars_cols_set = set(df.columns)
        missing_cols = [c for c in projections if c not in polars_cols_set]
        if len(missing_cols) > 0:
            raise KeyError(
                f"Attempted to select missing columns [{', '.join(sorted(missing_cols))}] "
                f"from DataFrame with columns [{', '.join(sorted(list(polars_cols_set)))}]"
            )

        df = df.select(projections)
    return df
