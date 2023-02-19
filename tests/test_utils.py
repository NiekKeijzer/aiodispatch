import importlib
import uuid

import pytest
from pytest_mock import MockerFixture

from aiodispatch.utils import generate_uuid, load_attribute

dummy_uuid = uuid.uuid4()


def test_uuid_generator(mocker: MockerFixture) -> None:
    patched = mocker.patch.object(uuid, "uuid4")

    generate_uuid()

    patched.assert_called_once()


def test_import_attribute(mocker: MockerFixture) -> None:
    patched = mocker.patch.object(importlib, "import_module")

    import_string = "foo:bar"

    load_attribute(import_string)

    patched.assert_called_with("foo")


def test_import_attribute_dummy() -> None:
    from tests.dummies.foo import bar as expected_bar

    import_string = "tests.dummies.foo:bar"
    bar = load_attribute(import_string)

    assert expected_bar == bar


def test_import_attribute_missing_dummy() -> None:
    import_string = "tests.dummies.foo:missing"

    with pytest.raises(ImportError):
        load_attribute(import_string)
