from dataclasses import dataclass

import pytest

import otit


@dataclass
class Address:
    city: str


@dataclass
class User:
    name: str
    address: Address


def test_dictionary() -> None:
    obj = {"user": {"name": "Matti"}}

    assert otit.get(obj, "user.name") == "Matti"


def test_list() -> None:
    obj = {"users": [{"name": "Matti"}]}

    assert otit.get(obj, "users.0.name") == "Matti"


def test_attributes() -> None:
    obj = User(
        name="Matti",
        address=Address(city="Oulu"),
    )

    assert otit.get(obj, "address.city") == "Oulu"


def test_mixed_structure() -> None:
    obj = {
        "users": [
            User(
                name="Matti",
                address=Address(city="Oulu"),
            )
        ]
    }

    assert otit.get(obj, "users.0.address.city") == "Oulu"


def test_missing_path() -> None:
    obj = {"user": {}}

    with pytest.raises(otit.PathNotFound):
        otit.get(obj, "user.name")


def test_default() -> None:
    obj = {"user": {}}

    assert otit.get(obj, "user.name", default=None) is None


def test_has() -> None:
    obj = {"user": {"name": "Matti"}}

    assert otit.has(obj, "user.name")
    assert not otit.has(obj, "user.email")
