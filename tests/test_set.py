from dataclasses import dataclass

import pytest

import otit


@dataclass
class User:
    name: str


def test_set_mapping_value() -> None:
    obj = {"user": {"name": "Matti"}}

    otit.set(obj, "user.name", "Liisa")

    assert obj["user"]["name"] == "Liisa"


def test_set_list_value() -> None:
    obj = {"users": ["Matti", "Liisa"]}

    otit.set(obj, "users.0", "Pekka")

    assert obj["users"][0] == "Pekka"


def test_set_attribute() -> None:
    obj = User(name="Matti")

    otit.set(obj, "name", "Liisa")

    assert obj.name == "Liisa"


def test_set_mixed_structure() -> None:
    obj = {"users": [User(name="Matti")]}

    otit.set(obj, "users.0.name", "Liisa")

    assert obj["users"][0].name == "Liisa"


def test_set_missing_mapping_key_fails_by_default() -> None:
    obj = {"user": {"name": "Matti"}}

    with pytest.raises(otit.PathNotFound):
        otit.set(obj, "user.email", "matti@example.com")


def test_set_can_create_mapping_key() -> None:
    obj = {"user": {"name": "Matti"}}

    otit.set(
        obj,
        "user.email",
        "matti@example.com",
        create=True,
    )

    assert obj["user"]["email"] == "matti@example.com"


def test_set_missing_attribute_fails_by_default() -> None:
    obj = User(name="Matti")

    with pytest.raises(otit.PathNotFound):
        otit.set(obj, "email", "matti@example.com")


def test_set_can_create_attribute() -> None:
    obj = User(name="Matti")

    otit.set(
        obj,
        "email",
        "matti@example.com",
        create=True,
    )

    assert obj.email == "matti@example.com"  # type: ignore[attr-defined]


def test_set_missing_parent_fails_even_with_create() -> None:
    obj: dict[str, object] = {}

    with pytest.raises(otit.PathNotFound):
        otit.set(
            obj,
            "user.name",
            "Matti",
            create=True,
        )


def test_set_out_of_range_list_index_fails() -> None:
    obj = {"users": ["Matti"]}

    with pytest.raises(otit.PathNotFound):
        otit.set(obj, "users.5", "Liisa")


def test_set_out_of_range_list_index_fails_with_create() -> None:
    obj = {"users": ["Matti"]}

    with pytest.raises(otit.PathNotFound):
        otit.set(
            obj,
            "users.5",
            "Liisa",
            create=True,
        )


def test_set_invalid_list_index_fails() -> None:
    obj = {"users": ["Matti"]}

    with pytest.raises(otit.PathNotFound):
        otit.set(obj, "users.foo", "Liisa")


def test_set_root_fails() -> None:
    obj = {"name": "Matti"}

    with pytest.raises(otit.InvalidPath):
        otit.set(obj, "", {})


def test_set_empty_tuple_path_fails() -> None:
    obj = {"name": "Matti"}

    with pytest.raises(otit.InvalidPath):
        otit.set(obj, (), {})
