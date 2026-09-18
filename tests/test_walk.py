from dataclasses import dataclass

import otit


@dataclass
class User:
    name: str


def test_walk_mapping() -> None:
    obj = {
        "user": {
            "name": "Matti",
        }
    }

    result = list(otit.walk(obj))

    assert result == [
        (("user",), {"name": "Matti"}),
        (("user", "name"), "Matti"),
    ]


def test_walk_sequence() -> None:
    obj = ["Matti", "Liisa"]

    result = list(otit.walk(obj))

    assert result == [
        ((0,), "Matti"),
        ((1,), "Liisa"),
    ]


def test_walk_mixed_structure() -> None:
    obj = {
        "users": [
            User(name="Matti"),
        ]
    }

    result = list(otit.walk(obj))

    assert result == [
        (("users",), [User(name="Matti")]),
        (("users", 0), User(name="Matti")),
        (("users", 0, "name"), "Matti"),
    ]
