from __future__ import annotations
from typing import Generic, TypeVar, Optional as Opt, Callable, Any, Type, cast


T = TypeVar("T")
R = TypeVar("R")


class PyOptional(Generic[T]):
    '''
    A container object which may or may not contain a non-`None` value. If a value is present, `is_present()` returns `True`. If no value is present, the object is considered empty and `is_present()` returns `False`.

    Additional methods that depend on the presence or absence of a contained value are provided, such as `or_else()` (returns a default value if no value is present) and `if_present()` (performs an action if a value is present).
    '''
    __CREATE_KEY: Any = object()

    def __init__(self, key: Any, val: Opt[T]=None) -> None:
        if key != PyOptional.__CREATE_KEY:
            raise TypeError("Cannot instantiate a `PyOptional` object. Use `PyOptional.empty()`, `PyOptional.of()`, or `PyOptional.of_nullable()` instead.")
        else:
            super().__init__()

            self.__val: Opt[T] = val

    @classmethod
    def empty(cls: Type[PyOptional[T]]) -> PyOptional[T]:
        '''
        Returns an empty `PyOptional` instance.

        There is no guarantee that a call to `PyOptional.empty()` will return a new instance or the same instance each time.

        Parameters:
            `cls: (Type[PyOptional[T]])`: The type of the non-existent value.
        Returns:
            An empty `PyOptional[T]`.
        '''
        return PyOptional[T](cls.__CREATE_KEY)

    @classmethod
    def of(cls: Type[PyOptional[T]], val: T) -> PyOptional[T]:
        '''
        Returns a `PyOptional` describing the given non-`None` value.

        If the given value is `None`, an `ValueError` is raised.
        '''
        if val is None:
            raise ValueError("Cannot create a `PyOptional` with a `None` value. Use `PyOptional.empty()` instead.")
        else:
            return PyOptional(cls.__CREATE_KEY, val)

    @classmethod
    def of_nullable(cls: Type[PyOptional[T]], val: Opt[T]) -> PyOptional[T]:
        '''
        Returns a `PyOptional` describing the given value if such value is non-`None`, otherwise returns an empty `PyOptional`.
        '''
        if val is None:
            return PyOptional.empty()
        else:
            return PyOptional(cls.__CREATE_KEY, val)

    def is_empty(self) -> bool:
        '''
        If a value is not present, returns `True`, otherwise `False`.
        '''
        return self.__val is None

    def is_present(self) -> bool:
        '''
        If a value is present, returns `True`, otherwise `False`.
        '''
        return self.__val is not None

    def if_present(self, fn: Callable[[T], Any]) -> None:
        '''
        If a value is present, performs the given action (i.e., applies `fn`) with the value, otherwise does nothing.
        '''
        if self.is_present():
            assert self.__val is not None

            fn(self.__val)

    def if_present_or_else(self, fn: Callable[[T], Any], empty_fn: Callable[[], None]) -> None:
        '''
        If a value is present, calls `fn` with the value as argument, otherwise calls `empty_fn` with no arguments.
        '''
        if self.is_present():
            assert self.__val is not None

            fn(self.__val)
        else:
            empty_fn()

    def filter(self, fn: Callable[[T], bool]) -> PyOptional[T]:
        '''
        If a value is present, and the value matches the given predicate, returns a `PyOptional` describing the value, otherwise returns an empty `PyOptional`.
        '''
        if self.is_present():
            assert self.__val is not None

            return self if fn(self.__val) else PyOptional.empty()
        else:
            return PyOptional.empty()

    def map(self, fn: Callable[[T], R]) -> PyOptional[R]:
        '''
        If a value is present, returns a `PyOptional` describing (as if by `of_nullable(T)`) the result of applying the given mapping function (i.e., `fn`) to the value, otherwise returns an empty `PyOptional`.
        '''
        if self.is_present():
            assert self.__val is not None

            return PyOptional.of_nullable(fn(self.__val))
        else:
            return PyOptional[R].empty()

    def flat_map(self, fn: Callable[[T], R]) -> PyOptional[R]:
        '''
        If a value is present, returns the result of applying the given `PyOptional`-bearing mapping function (i.e., `fn`) to the value, otherwise returns an empty `PyOptional`.

        In practice, this method does not wrap the result of the mapping function in an `PyOptional` instance if such result is already a `PyOptional`.
        '''
        if self.is_empty():
            return PyOptional[R].empty()
        else:
            assert self.__val is not None

            to_return: Any = fn(self.__val)

            return cast(PyOptional[R], to_return) if to_return is not None and isinstance(to_return, PyOptional) else PyOptional.of_nullable(to_return)

    def get(self) -> T:
        '''
        If a value is present, returns the value, otherwise raises a `ValueError`.
        '''
        if self.is_empty():
            raise ValueError("Cannot get the value of an empty `PyOptional`.")
        else:
            assert self.__val is not None

            return self.__val

    def or_else(self, default: T) -> T:
        '''
        If a value is present, returns the value, otherwise returns `default`.

        It is possible for `default` to be `None`.

        WARNING: `type(default)` can be anything.
        '''
        if not self.is_empty():
            return self.get()
        else:
            return default

    def or_else_get(self, fn: Callable[[], T]) -> T:
        '''
        If a value is present, returns the value, otherwise returns the result produced by the supplying function (i.e., `fn`).

        WARNING: the type of the return value of `fn` can be anything.
        '''
        if self.is_present():
            return self.get()
        else:
            return fn()

    def or_else_raise(self, exception: Opt[Exception | Any]=None) -> T:
        '''
        If a value is present, returns the value, otherwise raises the exception provided (i.e., `exception`) or `ValueError` if no `exception` is provided (or is `None`).
        '''
        if self.is_empty() and exception is not None and isinstance(exception, Exception):
            raise exception
        elif self.is_empty() and exception is not None:
            raise TypeError("Cannot raise a non-`Exception` object.")
        elif self.is_empty():
            raise ValueError("Cannot get the value of an empty `PyOptional`.")
        else:
            return self.get()

    or_else_throw = or_else_raise
    '''Convenient alias for `or_else_raise`.'''

    def or_new_pyoptional(self, fn: Callable[[], PyOptional[T]]) -> PyOptional[T]:
        '''
        If a value is present, returns a `PyOptional` describing the value, otherwise returns a `PyOptional` produced by the supplying function (i.e, `fn`).
        '''
        if self.is_present():
            return PyOptional.of_nullable(self.get())
        else:
            return fn()

    def __eq__(self, o: Any) -> bool:
        '''
        Returns `True` if `o` is equal to this `PyOptional`, `False` otherwise.

        Two `PyOptional` instances are equal if and only if they are both empty or both are non-empty and their values are equal.
        '''
        if o is None:
            return False
        elif not isinstance(o, PyOptional):
            return False
        else:
            return self.is_empty() and o.is_empty() or self.is_present() and o.is_present() and self.__val == cast(T, o.or_else_raise())

    def __hash__(self) -> int:
        '''
        Returns the `int` hash code of the value, if present, otherwise 0 (zero) if no value is present.
        '''
        return 0 if self.is_empty() else hash(self.__val)

    def __repr__(self) -> str:
        '''
        Returns a non-empty string representation of this `PyOptional`.
        '''
        return "PyOptional.empty()" if self.is_empty() else f"PyOptional.of({self.__val})"

    def __str__(self) -> str:
        '''
        Returns a non-empty string representation of this `PyOptional`.
        '''
        return "PyOptional.empty()" if self.is_empty() else f"PyOptional.of({self.__val})"
