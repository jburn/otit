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


def test_omit_does_not_modify_original() -> None:
    obj = {
        "user": {
            "name": "Matti",
            "password": "secret",
        }
    }

    otit.omit(obj, "user.password")

    assert obj == {
        "user": {
            "name": "Matti",
            "password": "secret",
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

def test_omit_sequence_paths_are_applied_in_order() -> None:
    obj = ["a", "b", "c"]

    result = otit.omit(
        obj,
        (1,),
        (1,),
    )

    assert result == ["a"]
