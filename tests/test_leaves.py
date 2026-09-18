from dataclasses import dataclass

import otit


@dataclass
class User:
    name: str
    age: int


def test_leaves_mapping() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "age": 30,
        }
    }

    assert list(otit.leaves(obj)) == [
        (("user", "name"), "Matti"),
        (("user", "age"), 30),
    ]


def test_leaves_sequence() -> None:
    obj = ["Matti", "Liisa"]

    assert list(otit.leaves(obj)) == [
        ((0,), "Matti"),
        ((1,), "Liisa"),
    ]


def test_leaves_mixed_structure() -> None:
    obj = {
        "users": [
            User(name="Matti", age=30),
        ]
    }

    assert list(otit.leaves(obj)) == [
        (("users", 0, "name"), "Matti"),
        (("users", 0, "age"), 30),
    ]


def test_leaves_empty_mapping() -> None:
    assert list(otit.leaves({})) == []


def test_leaves_empty_sequence() -> None:
    assert list(otit.leaves([])) == []


def test_leaves_nested_empty_containers() -> None:
    obj = {
        "empty_dict": {},
        "empty_list": [],
    }

    assert list(otit.leaves(obj)) == []


def test_leaves_scalar_root() -> None:
    assert list(otit.leaves("Matti")) == []

def test_leaves_handles_cycles() -> None:
    obj: dict[str, object] = {
        "name": "Matti",
    }
    obj["self"] = obj

    assert list(otit.leaves(obj)) == [
        (("name",), "Matti"),
    ]
