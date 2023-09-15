from typing import TypeVar, Generic, Literal, Union, Protocol

T = TypeVar('T')
E = TypeVar('E')


class Result(Generic[T, E]):
    """A generic, Rust-inspired Result class used for returning either a successful result or a list of errors."""

    __ok: T | None
    __err: list[E] | None

    @classmethod
    def ok(cls, result: T):
        return cls('ok', result)

    @classmethod
    def error(cls, *errors: Union['Result', Exception]):
        errors_ = []
        for maybe_err in errors:
            if isinstance(maybe_err, Exception):
                errors_.append(Result.error(maybe_err))
            else:
                assert isinstance(maybe_err, Result), 'Expected either an Exception or Result type.'
        return cls('error', errors_)

    def __init__(self, status: Literal['ok', 'error'], contents: T | list[E] | None):
        if status == 'ok':
            self.__ok = contents
            self.__err = None
        else:
            self.__err = contents
            self.__ok = None

    def status_and_value(self) -> Union[(Literal['ok'], T), (Literal['error'], E)]:
        if self.__ok:
            return 'ok', self.__ok
        else:
            return 'error', self.__err

    def is_err(self):
        return bool(self.__err)

    def is_ok(self):
        return bool(self.__ok)
