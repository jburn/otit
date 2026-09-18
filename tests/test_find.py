from dataclasses import dataclass
import pytest

import otit


@dataclass
class User:
    name: str
    age: int


def test_find_value() -> None:
    obj = {
        "users": [
            {"name": "Matti"},
            {"name": "Liisa"},
        ]
    }

    result = list(
        otit.find(obj, lambda value: value == "Matti")
    )

    assert result == [
        (("users", 0, "name"), "Matti"),
    ]


def test_find_multiple_values() -> None:
    obj = {
        "first": 10,
        "second": 20,
        "third": 30,
    }

    result = list(
        otit.find(
            obj,
            lambda value: isinstance(value, int) and value >= 20,
        )
    )

    assert result == [
        (("second",), 20),
        (("third",), 30),
    ]


def test_find_no_matches() -> None:
    obj = {
        "name": "Matti",
        "city": "Oulu",
    }

    result = list(
        otit.find(obj, lambda value: value == "Helsinki")
    )

    assert result == []


def test_find_attributes() -> None:
    obj = User(name="Matti", age=30)

    result = list(
        otit.find(obj, lambda value: value == "Matti")
    )

    assert result == [
        (("name",), "Matti"),
    ]


def test_find_container_values() -> None:
    obj = {
        "user": {
            "name": "Matti",
        }
    }

    result = list(
        otit.find(obj, lambda value: isinstance(value, dict))
    )

    assert result == [
        (("user",), {"name": "Matti"}),
    ]

def test_find_does_not_hide_predicate_exceptions() -> None:
    obj = {"value": 42}

    def predicate(value: object) -> bool:
        raise RuntimeError("predicate failed")

    with pytest.raises(RuntimeError, match="predicate failed"):
        list(otit.find(obj, predicate))