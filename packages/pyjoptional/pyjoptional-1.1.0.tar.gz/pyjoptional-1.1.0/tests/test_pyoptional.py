from __future__ import annotations
from typing import Any
from unittest import TestCase, main

from pyoptional.pyoptional import PyOptional


class TestPyOptional(TestCase):
    '''
    Tests for `PyOptional`.
    '''

    def test_illegal_creation(self) -> None:
        '''
        Tests that `PyOptional` cannot be created by invoking the constructor directly.
        '''
        self.assertRaises(TypeError, PyOptional)

        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            self.assertRaises(TypeError, PyOptional, content)

    def test_empty(self) -> None:
        '''
        Tests that `PyOptional.empty()` returns an empty `PyOptional`.
        '''
        self.assertRaises(ValueError, PyOptional.empty().get)

    def test_of(self) -> None:
        '''
        Tests that `PyOptional.of()` returns a non-empty `PyOptional` with the provided content.
        '''
        for content in [0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            self.assertEqual(PyOptional.of(content).get(), content)

        self.assertRaises(ValueError, PyOptional.of, None)

    def test_of_nullable(self) -> None:
        '''
        Tests that `PyOptional.of_nullable()` returns a non-empty `PyOptional` with the provided content if it is not `None`, otherwise returns an empty `PyOptional`.
        '''
        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertEqual(PyOptional.of_nullable(content).get(), content)
            else:
                self.assertRaises(ValueError, PyOptional.of_nullable(content).get)

    def test_is_empty(self) -> None:
        '''
        Tests that `PyOptional.is_empty()` returns `True` if the `PyOptional` is empty, and `False` otherwise.
        '''
        self.assertTrue(PyOptional.empty().is_empty())
        self.assertTrue(PyOptional.of_nullable(None).is_empty())

        for content in [0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            self.assertFalse(PyOptional.of(content).is_empty())
            self.assertFalse(PyOptional.of_nullable(content).is_empty())

    def test_is_present(self) -> None:
        '''
        Tests that `PyOptional.is_present()` returns `False` if the `PyOptional` is empty, and `True` otherwise.
        '''
        self.assertFalse(PyOptional.empty().is_present())
        self.assertFalse(PyOptional.of_nullable(None).is_present())

        for content in [0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            self.assertTrue(PyOptional.of(content).is_present())
            self.assertTrue(PyOptional.of_nullable(content).is_present())

    def test_if_present(self) -> None:
        '''
        Tests that `PyOptional.if_present()` invokes the provided function with the content of the `PyOptional` if it is not empty, doing nothing otherwise.
        '''
        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            def fn(x: Any, content: Any=content) -> None:
                self.assertIsNotNone(x)
                self.assertEqual(x, content)

            if content is not None:
                PyOptional.of(content).if_present(fn=fn)
                PyOptional.of_nullable(content).if_present(fn=fn)
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).if_present(fn=fn)

                PyOptional.of_nullable(content).if_present(fn=fn)

    def test_if_present_or_else(self) -> None:
        '''
        Tests that `PyOptional.if_present_or_else()` invokes the first provided function with the content of the `PyOptional` if it is not empty, and otherwise invokes the second provided function with no arguments.
        '''
        class EmptyException(Exception):
            pass

        class NonEmptyException(Exception):
            pass

        def fn(x: Any) -> None:
            self.assertIsNotNone(x)

            raise NonEmptyException()

        def empty_fn() -> None:
            raise EmptyException()

        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertRaises(NonEmptyException, PyOptional.of(content).if_present_or_else, fn, empty_fn)
                self.assertRaises(NonEmptyException, PyOptional.of_nullable(content).if_present_or_else, fn, empty_fn)
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).if_present_or_else(fn=fn, empty_fn=empty_fn)

                self.assertRaises(EmptyException, PyOptional.of_nullable(content).if_present_or_else, fn, empty_fn)

    def test_filter(self) -> None:
        '''
        Tests that `PyOptional.filter()` returns a non-empty `PyOptional` with the content of the `PyOptional` if the provided function returns `True` when invoked with the content of the `PyOptional`, and otherwise returns an empty `PyOptional`.
        '''
        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            def fn(x: Any, content: Any=content) -> bool:
                return x == content

            def fn2(x: Any, content: Any=content) -> bool:
                return x != content

            if content is not None:
                self.assertEqual(PyOptional.of(content).filter(fn=fn).get(), content)
                self.assertEqual(PyOptional.of_nullable(content).filter(fn=fn).get(), content)
                self.assertRaises(ValueError, PyOptional.of(content).filter(fn=fn2).get)
                self.assertRaises(ValueError, PyOptional.of_nullable(content).filter(fn=fn2).get)
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).filter(fn=fn)

                with self.assertRaises(ValueError):
                    PyOptional.of(content).filter(fn=fn2)

                with self.assertRaises(ValueError):
                    PyOptional.of(content).filter(fn=fn).get()

                self.assertRaises(ValueError, PyOptional.of_nullable(content).filter(fn=fn2).get)

    def test_map(self) -> None:
        '''
        Tests that `PyOptional.map()` returns a non-empty `PyOptional` with the result of invoking the provided function with the content of the `PyOptional` if the `PyOptional` is not empty, and otherwise returns an empty `PyOptional`.
        '''
        def map1(x: Any) -> Any:
            return x

        def map2(x: Any) -> str:
            return f"content: {repr(x)}."

        def map3(x: Any) -> PyOptional:
            return PyOptional.of_nullable(x)

        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertEqual(PyOptional.of(content).map(fn=map1).get(), content)
                self.assertEqual(PyOptional.of_nullable(content).map(fn=map1).get(), content)
                self.assertEqual(PyOptional.of(content).map(fn=map2).get(), f"content: {repr(content)}.")
                self.assertEqual(PyOptional.of_nullable(content).map(fn=map2).get(), f"content: {repr(content)}.")
                self.assertEqual(PyOptional.of(content).map(fn=map3).get(), PyOptional.of(content))
                self.assertEqual(PyOptional.of_nullable(content).map(fn=map3).get(), PyOptional.of_nullable(content))
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).map(fn=map1).get()

                with self.assertRaises(ValueError):
                    PyOptional.of_nullable(content).map(fn=map1).get()

                with self.assertRaises(ValueError):
                    PyOptional.of(content).map(fn=map2).get()

                with self.assertRaises(ValueError):
                    PyOptional.of_nullable(content).map(fn=map2).get()

                with self.assertRaises(ValueError):
                    PyOptional.of(content).map(fn=map3).get()

                with self.assertRaises(ValueError):
                    PyOptional.of_nullable(content).map(fn=map3).get()

    def test_flat_map(self) -> None:
        '''
        Tests that `PyOptional.flat_map()` returns a non-empty flattened (i.e., not unnecessarily wrapped in `PyOptional`) `PyOptional` with the result of invoking the provided function with the content of the `PyOptional` if the `PyOptional` is not empty, and otherwise returns an empty `PyOptional`.
        '''
        def map1(x: Any) -> Any:
            return x

        def map2(x: Any) -> str:
            return f"content: {repr(x)}."

        def map3(x: Any) -> PyOptional:
            return PyOptional.of_nullable(x)

        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertEqual(PyOptional.of(content).flat_map(fn=map1).get(), content)
                self.assertEqual(PyOptional.of_nullable(content).flat_map(fn=map1).get(), content)
                self.assertEqual(PyOptional.of(content).flat_map(fn=map2).get(), f"content: {repr(content)}.")
                self.assertEqual(PyOptional.of_nullable(content).flat_map(fn=map2).get(), f"content: {repr(content)}.")
                self.assertEqual(PyOptional.of(content).flat_map(fn=map3).get(), content)
                self.assertEqual(PyOptional.of_nullable(content).flat_map(fn=map3).get(), content)
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).flat_map(fn=map1).get()

                with self.assertRaises(ValueError):
                    PyOptional.of_nullable(content).flat_map(fn=map1).get()

                with self.assertRaises(ValueError):
                    PyOptional.of(content).flat_map(fn=map2).get()

                with self.assertRaises(ValueError):
                    PyOptional.of(content).flat_map(fn=map2).get()

                with self.assertRaises(ValueError):
                    PyOptional.of(content).flat_map(fn=map3).get()

                with self.assertRaises(ValueError):
                    PyOptional.of_nullable(content).flat_map(fn=map3).get()

    def test_get(self) -> None:
        '''
        Tests that `PyOptional.get()` returns the content of the `PyOptional` if the `PyOptional` is not empty, and otherwise raises a `ValueError`.
        '''
        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertEqual(PyOptional.of(content).get(), content)
                self.assertEqual(PyOptional.of_nullable(content).get(), content)
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).get()

                with self.assertRaises(ValueError):
                    PyOptional.of_nullable(content).get()

    def test_or_else(self) -> None:
        '''
        Tests that `PyOptional.or_else()` returns the content of the `PyOptional` if the `PyOptional` is not empty, and otherwise returns the provided default value.
        '''
        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertEqual(PyOptional.of(content).or_else(default=1), content)
                self.assertEqual(PyOptional.of_nullable(content).or_else(default=1), content)
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).or_else(default=1)

                self.assertEqual(PyOptional.of_nullable(content).or_else(default=1), 1)

    def test_or_else_get(self) -> None:
        '''
        Tests that `PyOptional.or_else_get()` returns the content of the `PyOptional` if the `PyOptional` is not empty, and otherwise returns the result of invoking the provided function.
        '''
        def fn() -> int:
            return 1

        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertEqual(PyOptional.of(content).or_else_get(fn=lambda: 1), content)
                self.assertEqual(PyOptional.of_nullable(content).or_else_get(fn=lambda: 1), content)
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).or_else_get(fn=fn)

                self.assertEqual(PyOptional.of_nullable(content).or_else_get(fn=fn), 1)

    def test_or_else_raise(self) -> None:
        '''
        Tests that `PyOptional.or_else_raise()` returns the content of the `PyOptional` if the `PyOptional` is not empty, and otherwise raises the provided exception (or `ValueError` if no exception was provided).
        '''
        class MyException(Exception):
            pass

        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertEqual(PyOptional.of(content).or_else_raise(exception=ValueError()), content)
                self.assertEqual(PyOptional.of_nullable(content).or_else_raise(exception=ValueError()), content)
                self.assertEqual(PyOptional.of(content).or_else_raise(exception=MyException()), content)
                self.assertEqual(PyOptional.of_nullable(content).or_else_raise(exception=MyException()), content)
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).or_else_raise()

                with self.assertRaises(ValueError):
                    PyOptional.of_nullable(content).or_else_raise()

                with self.assertRaises(ValueError):  # This is intended.
                    PyOptional.of(content).or_else_raise(exception=MyException())

                with self.assertRaises(MyException):
                    PyOptional.of_nullable(content).or_else_raise(exception=MyException())

    def test_or_new_pyoptional(self) -> None:
        '''
        tests that `PyOptional.or_new_pyoptional()` returns a `PyOptional` with the same content of the `PyOptional` if the `PyOptional` is not empty, and otherwise returns a new `PyOptional` which is the result of invoking the provided function.
        '''
        def fn() -> PyOptional:
            return PyOptional.of(1)

        for content in [None, 0, -1.2, False, "foo", b"foo", ["bar"], {1: "foobar"}, set(["a", "b", "c"]), (1, 2, 3), object()]:
            if content is not None:
                self.assertEqual(PyOptional.of(content).or_new_pyoptional(fn=fn), PyOptional.of(content))
                self.assertEqual(PyOptional.of_nullable(content).or_new_pyoptional(fn=fn), PyOptional.of(content))
            else:
                with self.assertRaises(ValueError):
                    PyOptional.of(content).or_new_pyoptional(fn=fn)

                self.assertEqual(PyOptional.of_nullable(content).or_new_pyoptional(fn=fn), PyOptional.of(1))


if __name__ == "__main__":
    main()
