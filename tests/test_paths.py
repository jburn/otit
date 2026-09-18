from dataclasses import dataclass

import otit


@dataclass
class User:
    name: str


def test_paths_mapping() -> None:
    obj = {
        "user": {
            "name": "Matti",
        }
    }

    assert list(otit.paths(obj)) == [
        ("user",),
        ("user", "name"),
    ]


def test_paths_sequence() -> None:
    obj = ["Matti", "Liisa"]

    assert list(otit.paths(obj)) == [
        (0,),
        (1,),
    ]


def test_paths_mixed_structure() -> None:
    obj = {
        "users": [
            User(name="Matti"),
        ]
    }

    assert list(otit.paths(obj)) == [
        ("users",),
        ("users", 0),
        ("users", 0, "name"),
    ]


def test_paths_empty_mapping() -> None:
    assert list(otit.paths({})) == []


def test_paths_empty_sequence() -> None:
    assert list(otit.paths([])) == []

def test_paths_handles_cycles() -> None:
    obj: dict[str, object] = {}
    obj["self"] = obj

    assert list(otit.paths(obj)) == [
        ("self",),
    ]

def test_paths_allows_shared_objects() -> None:
    shared = {"name": "Matti"}

    obj = {
        "first": shared,
        "second": shared,
    }

    assert list(otit.paths(obj)) == [
        ("first",),
        ("first", "name"),
        ("second",),
        ("second", "name"),
    ]
