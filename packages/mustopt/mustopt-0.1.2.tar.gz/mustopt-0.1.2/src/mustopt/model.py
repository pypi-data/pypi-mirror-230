from typing import Generic, Optional, TypeVar

T = TypeVar('T')


class MustOpt(Generic[T]):
    def __init__(self):
        self._value: Optional[T] = None
        self._valid: bool = False

    @staticmethod
    def new(value: Optional[T] = None) -> 'MustOpt[T]':
        res = MustOpt()
        res.set(value)
        return res

    def valid(self) -> bool:
        return self._valid

    def must(self) -> T:
        if not self._valid:
            msg = 'Underlying value is not valid'
            raise RuntimeError(msg)

        return self._value

    def set(self, value: Optional[T]):  # noqa: A003
        self._value = value
        self._valid = self._value is not None

    def unset(self):
        self._value = None
        self._valid = False
