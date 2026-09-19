# OTIT

**Object Traversal & Inspection Toolkit**

OTIT is a small, typed, dependency-free Python library for navigating, inspecting, and modifying heterogeneous nested Python objects.

It provides a consistent path-based API for working with mappings, sequences, object attributes, and structures containing a mixture of all three.

## Use cases

* API payload inspection - safely access deeply nested values without chains of dict/list indexing.
* Web scraping and extraction pipelines - inspect and extract values from nested structures produced by scrapers, parsers, or API responses.
* Configuration processing - inspect, test, modify, pick, or omit nested configuration values.
* Testing and assertions - query arbitrary nested structures with consistent path semantics.
* Data inspection/tooling - walk heterogeneous combinations of mappings, sequences, and Python objects.
* Payload shaping - use pick() and omit() to derive structures without modifying the original.
* Generic application utilities - work with nested structures when the exact mixture of dictionaries, lists, and objects isn't known in advance.

## Installation

```bash
pip install otit
```

Requires Python 3.10 or later.

## Quick start

```python
import otit

data = {
    "users": [
        {
            "name": "Matti",
            "address": {
                "city": "Oulu",
            },
        }
    ]
}

otit.get(data, "users.0.name")
# "Matti"

otit.get(data, "users.0.address.city")
# "Oulu"

otit.has(data, "users.0.email")
# False
```

Paths can also be given explicitly as sequences:

```python
otit.get(data, ("users", 0, "name"))
# "Matti"
```

Explicit paths are useful when a mapping key contains a dot or when preserving the exact type of a path segment matters.

```python
data = {"foo.bar": "value"}

otit.get(data, ("foo.bar",))
# "value"
```

## Getting values

Use `get()` to resolve a path:

```python
otit.get(data, "users.0.name")
# "Matti"
```

A default can be returned when the path does not exist:

```python
otit.get(data, "users.0.email", default=None)
# None
```

Without a default, an unresolved path raises `otit.PathNotFound`.

## Checking paths

Use `has()` to test whether a path can be resolved:

```python
otit.has(data, "users.0.name")
# True

otit.has(data, "users.0.email")
# False
```

## Setting values

Use `set()` to modify an existing value:

```python
otit.set(data, "users.0.name", "Liisa")
```

By default, the complete path must already exist.

Set `create=True` to allow creation of the final mapping key or object attribute:

```python
otit.set(
    data,
    "users.0.email",
    "liisa@example.com",
    create=True,
)
```

`create=True` does not create missing parent containers or extend sequences.

## Deleting values

Use `delete()` to remove a value:

```python
otit.delete(data, "users.0.address.city")
```

For mappings, the key is removed. For mutable sequences, the item is removed and subsequent indexes shift. For objects, the attribute is deleted.

## Walking objects

`walk()` recursively yields every reachable child together with its path:

```python
data = {
    "user": {
        "name": "Matti",
        "tags": ["admin", "active"],
    }
}

list(otit.walk(data))
```

produces:

```python
[
    (("user",), {"name": "Matti", "tags": ["admin", "active"]}),
    (("user", "name"), "Matti"),
    (("user", "tags"), ["admin", "active"]),
    (("user", "tags", 0), "admin"),
    (("user", "tags", 1), "active"),
]
```

Traversal paths use tuples. Sequence indexes are represented as integers.

The root object itself is not yielded.

## Finding values

Use `find()` to select reachable values with a predicate:

```python
list(
    otit.find(
        data,
        lambda value: isinstance(value, str) and value.startswith("M"),
    )
)
```

The result contains `(path, value)` pairs.

## Listing paths

Use `paths()` to iterate over every reachable path:

```python
list(otit.paths(data))
```

For example:

```python
[
    ("user",),
    ("user", "name"),
    ("user", "tags"),
    ("user", "tags", 0),
    ("user", "tags", 1),
]
```

## Finding leaves

Use `leaves()` to iterate over terminal values:

```python
list(otit.leaves(data))
```

For example:

```python
[
    (("user", "name"), "Matti"),
    (("user", "tags", 0), "admin"),
    (("user", "tags", 1), "active"),
]
```

Empty mappings and sequences are not considered leaves.

## Picking values

`pick()` creates a new structure containing only selected paths:

```python
data = {
    "user": {
        "name": "Matti",
        "email": "matti@example.com",
        "password": "secret",
    }
}

otit.pick(
    data,
    "user.name",
    "user.email",
)
```

returns:

```python
{
    "user": {
        "name": "Matti",
        "email": "matti@example.com",
    }
}
```

Selected sequence items are compacted while preserving their original order.

The original object is not modified.

## Omitting values

`omit()` creates a copy with selected paths removed:

```python
otit.omit(
    data,
    "user.password",
)
```

returns:

```python
{
    "user": {
        "name": "Matti",
        "email": "matti@example.com",
    }
}
```

All omitted paths refer to the original object. This means removing sequence items does not change the meaning of other paths passed in the same call.

The original object is not modified.

## Path semantics

A path may be a dot-separated string:

```python
"users.0.address.city"
```

or an explicit sequence:

```python
("users", 0, "address", "city")
```

OTIT resolves each segment according to the object currently being traversed:

* Mappings use the segment as a mapping key.
* Sequences interpret the segment as an integer index.
* Other objects use string segments as attribute names.
* Strings, bytes, and bytearrays are treated as terminal values rather than traversable sequences.
* Negative sequence indexes are supported.
* Numeric-looking mapping keys remain mapping keys.

For example:

```python
data = {
    "lookup": {
        "0": "zero",
    },
    "items": [
        "first",
    ],
}

otit.get(data, "lookup.0")
# "zero"

otit.get(data, "items.0")
# "first"
```

The meaning of `"0"` depends on the object being traversed.

## Root paths

The empty string and empty tuple represent the root object:

```python
otit.get(data, "") is data
# True

otit.has(data, ())
# True
```

Operations that require a target below the root, such as `set()`, `delete()`, `pick()`, and `omit()`, reject a root path with `otit.InvalidPath`.

## Exceptions

OTIT exposes a small exception hierarchy:

```text
OtitError
├── PathNotFound
└── InvalidPath
```

`PathNotFound` is raised when OTIT cannot resolve a requested path.

`InvalidPath` is raised when a path is structurally invalid for the requested operation.

Exceptions raised by user-defined properties or other object behavior are not converted into `PathNotFound`.

## Cycles and shared objects

Traversal functions detect cycles and do not recursively follow the same object through an active ancestor path.

Shared objects reachable through different paths are still traversed independently.

## Supported objects

OTIT is designed for heterogeneous structures containing:

* mappings such as `dict`
* sequences such as `list` and `tuple`
* regular Python objects
* dataclass instances
* mixtures of the above

Mutation requires the underlying object to support the requested operation.

## API

```python
otit.get(obj, path, *, default=...)
otit.has(obj, path)

otit.set(obj, path, value, *, create=False)
otit.delete(obj, path)

otit.walk(obj)
otit.find(obj, predicate)
otit.paths(obj)
otit.leaves(obj)

otit.pick(obj, *paths)
otit.omit(obj, *paths)
```

## Development

Install development dependencies:

```bash
uv sync
```

Run the test suite:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Run type checking:

```bash
uv run mypy src
```

Build the package:

```bash
uv build
```

## License

OTIT is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

See the LICENSE file for the full license text.
