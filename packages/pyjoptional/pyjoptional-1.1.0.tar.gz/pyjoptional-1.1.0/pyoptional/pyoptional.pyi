from __future__ import annotations
from typing import Generic, TypeVar, Optional as Opt, Callable, Any, Type


T = TypeVar("T")
R = TypeVar("R")


class PyOptional(Generic[T]):
    '''
    A container object which may or may not contain a non-`None` value. If a value is present, `is_present()` returns `True`. If no value is present, the object is considered empty and `is_present()` returns `False`.

    Additional methods that depend on the presence or absence of a contained value are provided, such as `or_else()` (returns a default value if no value is present) and `if_present()` (performs an action if a value is present).
    '''
    def __init__(self, key: Any, val: Opt[T]=None) -> None:
        ...

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
        ...

    @classmethod
    def of(cls: Type[PyOptional[T]], val: T) -> PyOptional[T]:
        '''
        Returns a `PyOptional` describing the given non-`None` value.

        If the given value is `None`, an `ValueError` is raised.
        '''
        ...

    @classmethod
    def of_nullable(cls: Type[PyOptional[T]], val: Opt[T]) -> PyOptional[T]:
        '''
        Returns a `PyOptional` describing the given value if such value is non-`None`, otherwise returns an empty `PyOptional`.
        '''
        ...

    def is_empty(self) -> bool:
        '''
        If a value is not present, returns `True`, otherwise `False`.
        '''
        ...

    def is_present(self) -> bool:
        '''
        If a value is present, returns `True`, otherwise `False`.
        '''
        ...

    def if_present(self, fn: Callable[[T], Any]) -> None:
        '''
        If a value is present, performs the given action (i.e., applies `fn`) with the value, otherwise does nothing.
        '''
        ...

    def if_present_or_else(self, fn: Callable[[T], Any], empty_fn: Callable[[], None]) -> None:
        '''
        If a value is present, calls `fn` with the value as argument, otherwise calls `empty_fn` with no arguments.
        '''
        ...

    def filter(self, fn: Callable[[T], bool]) -> PyOptional[T]:
        '''
        If a value is present, and the value matches the given predicate, returns a `PyOptional` describing the value, otherwise returns an empty `PyOptional`.
        '''
        ...

    def map(self, fn: Callable[[T], R]) -> PyOptional[R]:
        '''
        If a value is present, returns a `PyOptional` describing (as if by `of_nullable(T)`) the result of applying the given mapping function (i.e., `fn`) to the value, otherwise returns an empty `PyOptional`.
        '''
        ...

    def flat_map(self, fn: Callable[[T], R]) -> PyOptional[R]:
        '''
        If a value is present, returns the result of applying the given `PyOptional`-bearing mapping function (i.e., `fn`) to the value, otherwise returns an empty `PyOptional`.

        In practice, this method does not wrap the result of the mapping function in an `PyOptional` instance if such result is already a `PyOptional`.
        '''
        ...

    def get(self) -> T:
        '''
        If a value is present, returns the value, otherwise raises a `ValueError`.
        '''
        ...

    def or_else(self, default: T) -> T:
        '''
        If a value is present, returns the value, otherwise returns `default`.

        It is possible for `default` to be `None`.

        WARNING: `type(default)` can be anything.
        '''
        ...

    def or_else_get(self, fn: Callable[[], T]) -> T:
        '''
        If a value is present, returns the value, otherwise returns the result produced by the supplying function (i.e., `fn`).

        WARNING: the type of the return value of `fn` can be anything.
        '''
        ...

    def or_else_raise(self, exception: Opt[Exception]=None) -> T:
        '''
        If a value is present, returns the value, otherwise raises the exception provided (i.e., `exception`) or `ValueError` if no `exception` is provided (or is `None`).
        '''
        ...

    or_else_throw = or_else_raise
    '''Convenient alias for `or_else_raise`.'''

    def or_new_pyoptional(self, fn: Callable[[], PyOptional[T]]) -> PyOptional[T]:
        '''
        If a value is present, returns a `PyOptional` describing the value, otherwise returns a `PyOptional` produced by the supplying function (i.e, `fn`).
        '''
        ...

    def __eq__(self, o: Any) -> bool:
        '''
        Returns `True` if `o` is equal to this `PyOptional`, `False` otherwise.

        Two `PyOptional` instances are equal if and only if they are both empty or both are non-empty and their values are equal.
        '''
        ...

    def __hash__(self) -> int:
        '''
        Returns the `int` hash code of the value, if present, otherwise 0 (zero) if no value is present.
        '''
        ...

    def __repr__(self) -> str:
        '''
        Returns a non-empty string representation of this `PyOptional`.
        '''
        ...

    def __str__(self) -> str:
        '''
        Returns a non-empty string representation of this `PyOptional`.
        '''
        ...
