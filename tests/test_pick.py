import pytest

import otit


def test_pick_single_path() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "age": 30,
        }
    }

    assert otit.pick(obj, "user.name") == {
        ("user", "name"): "Matti",
    }


def test_pick_multiple_paths() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "age": 30,
        }
    }

    assert otit.pick(
        obj,
        "user.name",
        "user.age",
    ) == {
        ("user", "name"): "Matti",
        ("user", "age"): 30,
    }


def test_pick_sequence_path() -> None:
    obj = {
        "users": [
            {"name": "Matti"},
            {"name": "Liisa"},
        ]
    }

    assert otit.pick(
        obj,
        "users.1.name",
    ) == {
        ("users", "1", "name"): "Liisa",
    }


def test_pick_explicit_path_preserves_integer_segment() -> None:
    obj = {
        "users": [
            {"name": "Matti"},
        ]
    }

    assert otit.pick(
        obj,
        ("users", 0, "name"),
    ) == {
        ("users", 0, "name"): "Matti",
    }


def test_pick_missing_path_fails() -> None:
    obj = {"user": {"name": "Matti"}}

    with pytest.raises(otit.PathNotFound):
        otit.pick(
            obj,
            "user.email",
        )


def test_pick_no_paths() -> None:
    obj = {"name": "Matti"}

    assert not otit.pick(obj)
