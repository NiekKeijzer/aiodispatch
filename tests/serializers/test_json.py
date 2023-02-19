import json

from pytest_mock import MockerFixture

from aiotasq.serializers.json import JsonSerializer


def test_json_serializer_dumps(mocker: MockerFixture) -> None:
    patched = mocker.patch.object(json, "dumps")

    serializer = JsonSerializer()
    serializer.dumps({})

    patched.assert_called_with({})


def test_json_serializer_loads(mocker: MockerFixture) -> None:
    patched = mocker.patch.object(json, "loads")

    serializer = JsonSerializer()
    serializer.loads(b"{}")

    patched.assert_called_with(b"{}")
