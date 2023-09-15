from typing import Any


class Underscore:
    """
    An unevaluated underscore expression.
    Example usage:
    class X:
        y: DF[Y]
        s: int = _.y[_.z].sum()
    """

    def __getattr__(self, attr: str) -> "Underscore":
        if attr.startswith("__") or attr.startswith("_chalk__"):
            raise AttributeError(f"{self.__class__.__name__!r} {attr!r}")
        return UnderscoreAttr(self, attr)

    def __getitem__(self, key: Any) -> "Underscore":
        return UnderscoreItem(self, key)

    def __call__(self, *args: Any, **kwargs: Any) -> "Underscore":
        return UnderscoreCall(self, *args, **kwargs)

    def __add__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("+", self, other)

    def __radd__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("+", other, self)

    def __sub__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("-", self, other)

    def __rsub__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("-", other, self)

    def __mul__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("*", self, other)

    def __rmul__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("*", other, self)

    def __truediv__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("/", self, other)

    def __rtruediv__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("/", other, self)

    def __floordiv__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("//", self, other)

    def __rfloordiv__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("//", other, self)

    def __mod__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("%", self, other)

    def __rmod__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("%", other, self)

    def __pow__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("**", self, other)

    def __rpow__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("**", other, self)

    def __lt__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("<", self, other)

    def __le__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("<=", self, other)

    def __gt__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp(">", self, other)

    def __ge__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp(">=", self, other)

    def __eq__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("==", self, other)

    def __ne__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("!=", self, other)

    def __and__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("&", self, other)

    def __rand__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("&", other, self)

    def __or__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("|", self, other)

    def __ror__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("|", other, self)

    def __xor__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("^", self, other)

    def __rxor__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("^", other, self)

    def __lshift__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("<<", self, other)

    def __rlshift__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp("<<", other, self)

    def __rshift__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp(">>", self, other)

    def __rrshift__(self, other: Any) -> "Underscore":
        return UnderscoreBinaryOp(">>", other, self)

    def __neg__(self) -> "Underscore":
        return UnderscoreUnaryOp("-", self)

    def __pos__(self) -> "Underscore":
        return UnderscoreUnaryOp("+", self)

    def __invert__(self) -> "Underscore":
        return UnderscoreUnaryOp("~", self)


class UnderscoreRoot(Underscore):
    pass


class UnderscoreAttr(Underscore):
    def __init__(self, parent: Underscore, attr: str):
        self._chalk__parent = parent
        self._chalk__attr = attr


class UnderscoreItem(Underscore):
    def __init__(self, parent: Underscore, key: Any):
        self._chalk__parent = parent
        self._chalk__key = key


class UnderscoreCall(Underscore):
    def __init__(self, parent: Underscore, *args: Any, **kwargs: Any):
        self._chalk__parent = parent
        self._chalk__args = args
        self._chalk__kwargs = kwargs


class UnderscoreBinaryOp(Underscore):
    def __init__(self, op: str, left: Any, right: Any):
        self._chalk__op = op
        self._chalk__left = left
        self._chalk__right = right


class UnderscoreUnaryOp(Underscore):
    def __init__(self, op: str, operand: Any):
        self._chalk__op = op
        self._chalk__operand = operand


_ = underscore = UnderscoreRoot()
