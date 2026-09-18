from dataclasses import dataclass

import pytest

import otit


@dataclass
class User:
    name: str
    email: str


def test_delete_mapping_key() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "email": "matti@example.com",
        }
    }

    otit.delete(obj, "user.email")

    assert "email" not in obj["user"]


def test_delete_list_item() -> None:
    obj = {"users": ["Matti", "Liisa", "Pekka"]}

    otit.delete(obj, "users.1")

    assert obj["users"] == ["Matti", "Pekka"]


def test_delete_attribute() -> None:
    obj = User(
        name="Matti",
        email="matti@example.com",
    )

    otit.delete(obj, "email")

    assert not hasattr(obj, "email")


def test_delete_mixed_structure() -> None:
    obj = {
        "users": [
            {
                "name": "Matti",
                "tags": ["admin", "active"],
            }
        ]
    }

    otit.delete(obj, "users.0.tags.0")

    assert obj["users"][0]["tags"] == ["active"]


def test_delete_missing_mapping_key_fails() -> None:
    obj = {"user": {"name": "Matti"}}

    with pytest.raises(otit.PathNotFound):
        otit.delete(obj, "user.email")


def test_delete_missing_parent_fails() -> None:
    obj: dict[str, object] = {}

    with pytest.raises(otit.PathNotFound):
        otit.delete(obj, "user.name")


def test_delete_out_of_range_list_index_fails() -> None:
    obj = {"users": ["Matti"]}

    with pytest.raises(otit.PathNotFound):
        otit.delete(obj, "users.5")


def test_delete_invalid_list_index_fails() -> None:
    obj = {"users": ["Matti"]}

    with pytest.raises(otit.PathNotFound):
        otit.delete(obj, "users.foo")


def test_delete_missing_attribute_fails() -> None:
    obj = User(
        name="Matti",
        email="matti@example.com",
    )

    with pytest.raises(otit.PathNotFound):
        otit.delete(obj, "phone")


def test_delete_root_fails() -> None:
    obj = {"name": "Matti"}

    with pytest.raises(otit.InvalidPath):
        otit.delete(obj, "")


def test_delete_empty_tuple_path_fails() -> None:
    obj = {"name": "Matti"}

    with pytest.raises(otit.InvalidPath):
        otit.delete(obj, ())
