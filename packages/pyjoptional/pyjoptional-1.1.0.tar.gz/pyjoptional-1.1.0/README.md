# PyJOptional

A Python module providing the `PyOptional` class/type, a Java-like `Optional` wrapper for Python values.

## HOWTO

```console
user@machine:~$ pip install pyjoptional
```

```python
from pyoptional.pyoptional import PyOptional

p: PyOptional[int] = PyOptional.of(1)
p1: PyOptional = PyOptional.of_nullable(None)
p2: PyOptional = PyOptional.empty()
```

## Comparison with the Java `Optional`

* `PyOptional.of()` corresponds to `Optional.of()`.
* `PyOptional.of_nullable()` corresponds to `Optional.ofNullable()`.
* `PyOptional.empty()` corresponds to `Optional.empty()`.
* `PyOptional.is_empty()` corresponds to `Optional.isEmpty()`.
* `PyOptional.is_present()` corresponds to `Optional.isPresent()`.
* `PyOptional.filter()` corresponds to `Optional.filter()`.
* `PyOptional.get()` corresponds to `Optional.get()`.
* `PyOptional.or_else()` corresponds to `Optional.orElse()`.
* `PyOptional.or_else_get()` corresponds to `Optional.orElseGet()`.
* `PyOptional.or_else_raise()` corresponds to `Optional.orElseThrow()` (both with and without a supplied `Exception`).
* `PyOptional.or_else_throw` is an alias of `Optional.or_else_raise`.
* `PyOptional.or_new_pyoptional()` corresponds to `Optional.or()` (because `or` is a Python keyword).
* `PyOptional.if_present()` corresponds to `Optional.ifPresent()`.
* `PyOptional.if_present_or_else()` corresponds to `Optional.ifPresentOrElse()`.
* `PyOptional.map()` corresponds to `Optional.map()`.
* `PyOptional.flatMap()` corresponds to `Optional.flatMap()`.

Additionally, `PyOptional.__eq__`, `PyOptional.__hash__`, `PyOptional.__str__`, and `PyOptional.__repr__` override the default Python implementation of such methods, much like the Java `Optional.equals()`, `Optional.hashCode()`, and `Optional.toString()` methods.

Finally, there is no correspondent of the Java `Optional.stream()` method, as Python has no native `Stream` class.

## Comparison with the Python `Optional`

The native Python `Optional[SomeType]` type is just syntactic sugar for `SomeType | None`. Therefore, it does not provide any of the API methods of `PyOptional`.
