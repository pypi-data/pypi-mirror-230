from typing import TypeVar, Protocol, runtime_checkable

T = TypeVar("T")
E = TypeVar("E")


@runtime_checkable
class Result(Protocol[T]):
    def __eq__(self, other) -> bool:
        ...

    def is_ok(self) -> bool:
        ...

    def is_err(self) -> bool:
        ...

    def tuple(self) -> (str, T):
        ...


class Ok(Result[T]):
    __match_args__ = ('value',)
    value: T

    def __init__(self, value: T):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Ok) and self.value == other.value:
            return True
        else:
            return False

    def is_err(self):
        return False

    def is_ok(self):
        return True

    def tuple(self) -> (str, T):
        return "ok", self.value


class Err(Result[E]):
    __match_args__ = ('err',)
    err: E

    def __init__(self, err: E):
        self.err = err

    def __eq__(self, other) -> bool:
        if isinstance(other, Err) and self.err == other.err:
            return True
        else:
            return False

    def is_err(self) -> bool:
        return True

    def is_ok(self) -> bool:
        return False

    def tuple(self) -> (str, E):
        return "err", self.err
