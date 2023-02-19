from aiotasq.enums import Route


def test_enum_as_string() -> None:
    assert "TASKS" == str(Route.TASKS)
