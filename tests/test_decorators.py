from pytest_mock import MockerFixture

from aiotasq.decorators import task as task_decorator
from aiotasq.dispatch import Dispatcher
from aiotasq.tasks import Task


async def test_task_gets_published(
    mocker: MockerFixture, dispatcher: Dispatcher, task: Task
) -> None:
    patched = mocker.patch.object(dispatcher, "publish")

    @task_decorator()
    async def dummy() -> None:
        ...

    await dummy()

    patched.assert_called_once()
