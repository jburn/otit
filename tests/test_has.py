from dataclasses import dataclass

import otit


@dataclass
class User:
    name: str


def test_has_mapping_key() -> None:
    obj = {"user": {"name": "Matti"}}

    assert otit.has(obj, "user.name")


def test_has_missing_mapping_key() -> None:
    obj = {"user": {"name": "Matti"}}

    assert not otit.has(obj, "user.email")


def test_has_list_index() -> None:
    obj = {"users": ["Matti", "Liisa"]}

    assert otit.has(obj, "users.0")


def test_has_missing_list_index() -> None:
    obj = {"users": ["Matti"]}

    assert not otit.has(obj, "users.5")


def test_has_invalid_list_index() -> None:
    obj = {"users": ["Matti"]}

    assert not otit.has(obj, "users.foo")


def test_has_attribute() -> None:
    obj = User(name="Matti")

    assert otit.has(obj, "name")


def test_has_missing_attribute() -> None:
    obj = User(name="Matti")

    assert not otit.has(obj, "email")


def test_has_mixed_structure() -> None:
    obj = {
        "users": [
            User(name="Matti"),
        ]
    }

    assert otit.has(obj, "users.0.name")


def test_has_missing_intermediate_path() -> None:
    obj: dict[str, object] = {}

    assert not otit.has(obj, "user.name")


def test_has_root() -> None:
    obj = {"name": "Matti"}

    assert otit.has(obj, "")


def test_has_empty_tuple_path() -> None:
    obj = {"name": "Matti"}

    assert otit.has(obj, ())
