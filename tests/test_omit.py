import pytest

import otit


def test_omit_mapping_key() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "password": "secret",
        }
    }

    result = otit.omit(obj, "user.password")

    assert result == {
        "user": {
            "name": "Matti",
        }
    }


def test_omit_multiple_paths() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "email": "matti@example.com",
            "password": "secret",
        }
    }

    result = otit.omit(
        obj,
        "user.email",
        "user.password",
    )

    assert result == {
        "user": {
            "name": "Matti",
        }
    }


def test_omit_missing_path_fails() -> None:
    obj = {
        "user": {
            "name": "Matti",
        }
    }

    with pytest.raises(otit.PathNotFound):
        otit.omit(obj, "user.password")


def test_omit_no_paths_returns_copy() -> None:
    obj = {
        "user": {
            "name": "Matti",
        }
    }

    result = otit.omit(obj)

    assert result == obj
    assert result is not obj

def test_omit_duplicate_sequence_paths_are_redundant() -> None:
    obj = ["a", "b", "c"]

    result = otit.omit(
        obj,
        (1,),
        (1,),
    )

    assert result == ["a", "c"]

def test_omit_multiple_sequence_items_uses_original_indexes() -> None:
    obj = ["a", "b", "c", "d"]

    assert otit.omit(
        obj,
        (0,),
        (2,),
    ) == ["b", "d"]


def test_omit_sequence_order_does_not_matter() -> None:
    obj = ["a", "b", "c", "d"]

    first = otit.omit(
        obj,
        (0,),
        (2,),
    )

    second = otit.omit(
        obj,
        (2,),
        (0,),
    )

    assert first == second == ["b", "d"]


def test_omit_parent_subsumes_descendant() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "password": "secret",
        },
        "active": True,
    }

    assert otit.omit(
        obj,
        "user.password",
        "user",
    ) == {
        "active": True,
    }


def test_omit_parent_subsumes_descendant_regardless_of_order() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "password": "secret",
        },
        "active": True,
    }

    assert otit.omit(
        obj,
        "user",
        "user.password",
    ) == {
        "active": True,
    }


def test_omit_duplicate_paths() -> None:
    obj = {
        "name": "Matti",
        "age": 30,
    }

    assert otit.omit(
        obj,
        "age",
        "age",
    ) == {
        "name": "Matti",
    }


def test_omit_does_not_modify_original() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "password": "secret",
        }
    }

    result = otit.omit(
        obj,
        "user.password",
    )

    assert result == {
        "user": {
            "name": "Matti",
        }
    }

    assert obj == {
        "user": {
            "name": "Matti",
            "password": "secret",
        }
    }

def test_omit_nested_sequence_items() -> None:
    obj = {
        "groups": [
            {
                "users": ["a", "b", "c"],
            },
            {
                "users": ["d", "e", "f"],
            },
        ]
    }

    assert otit.omit(
        obj,
        "groups.0.users.0",
        "groups.0.users.2",
        "groups.1.users.1",
    ) == {
        "groups": [
            {
                "users": ["b"],
            },
            {
                "users": ["d", "f"],
            },
        ]
    }

def test_omit_sequence_paths_use_original_indexes() -> None:
    obj = ["a", "b", "c", "d"]

    result = otit.omit(
        obj,
        (0,),
        (2,),
    )

    assert result == ["b", "d"]

def test_omit_sequence_path_order_does_not_matter() -> None:
    obj = ["a", "b", "c", "d"]

    first = otit.omit(
        obj,
        (0,),
        (2,),
    )

    second = otit.omit(
        obj,
        (2,),
        (0,),
    )

    assert first == second == ["b", "d"]
