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
        "user": {
            "name": "Matti",
        }
    }


def test_pick_multiple_paths() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "age": 30,
            "email": "matti@example.com",
        }
    }

    assert otit.pick(
        obj,
        "user.name",
        "user.age",
    ) == {
        "user": {
            "name": "Matti",
            "age": 30,
        }
    }


def test_pick_sequence_item() -> None:
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
        "users": [
            {"name": "Liisa"},
        ]
    }


def test_pick_multiple_fields_from_same_sequence_item() -> None:
    obj = {
        "users": [
            {
                "name": "Matti",
                "age": 30,
                "password": "secret",
            }
        ]
    }

    assert otit.pick(
        obj,
        "users.0.name",
        "users.0.age",
    ) == {
        "users": [
            {
                "name": "Matti",
                "age": 30,
            }
        ]
    }


def test_pick_multiple_sequence_items_preserves_order() -> None:
    obj = {
        "users": [
            {"name": "Matti"},
            {"name": "Liisa"},
            {"name": "Teppo"},
        ]
    }

    assert otit.pick(
        obj,
        "users.2.name",
        "users.0.name",
    ) == {
        "users": [
            {"name": "Matti"},
            {"name": "Teppo"},
        ]
    }


def test_pick_missing_path_fails() -> None:
    obj = {"user": {"name": "Matti"}}

    with pytest.raises(otit.PathNotFound):
        otit.pick(obj, "user.email")


def test_pick_no_paths() -> None:
    assert otit.pick({"name": "Matti"}) == {}


def test_pick_root_path_fails() -> None:
    with pytest.raises(otit.InvalidPath):
        otit.pick({"name": "Matti"}, "")

def test_pick_deep_copies_values() -> None:
    obj = {
        "user": {
            "settings": {
                "theme": "dark",
            }
        }
    }

    result = otit.pick(obj, "user.settings")

    result["user"]["settings"]["theme"] = "light"

    assert obj["user"]["settings"]["theme"] == "dark"

def test_pick_integer_mapping_key() -> None:
    obj = {
        "lookup": {
            0: "zero",
            1: "one",
        }
    }

    assert otit.pick(
        obj,
        ("lookup", 0),
    ) == {
        "lookup": {
            0: "zero",
        }
    }


def test_pick_numeric_string_mapping_key() -> None:
    obj = {
        "lookup": {
            "0": "zero",
        }
    }

    assert otit.pick(
        obj,
        "lookup.0",
    ) == {
        "lookup": {
            "0": "zero",
        }
    }


def test_pick_sequence_index() -> None:
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
        "users": [
            {"name": "Liisa"},
        ]
    }

def test_pick_multiple_sequence_items() -> None:
    obj = {
        "users": [
            {"name": "Matti", "age": 30, "secret": "a"},
            {"name": "Liisa", "age": 25, "secret": "b"},
        ]
    }

    assert otit.pick(
        obj,
        "users.0.name",
        "users.0.age",
        "users.1.name",
        "users.1.age",
    ) == {
        "users": [
            {"name": "Matti", "age": 30},
            {"name": "Liisa", "age": 25},
        ]
    }
