from pytest_mock import MockerFixture

from aiodispatch.dispatch import Dispatcher
from aiodispatch.dispatch import dispatcher as _dispatcher
from aiodispatch.serializers.json import JsonSerializer
from aiodispatch.tasks import Task

from .utils import DummyAsyncIterator


def test_dispatcher_contextvar_set(dispatcher: Dispatcher) -> None:
    assert dispatcher == _dispatcher.get()


async def test_dispatcher_serializes_task(
    mocker: MockerFixture,
    dispatcher: Dispatcher,
    json_serializer: JsonSerializer,
    task: Task,
) -> None:
    task_dict = task.as_dict()
    serialized_task = json_serializer.dumps(task_dict)

    patched = mocker.patch.object(dispatcher.serializer, "dumps")
    patched.return_value = serialized_task
    await dispatcher.publish(task)

    patched.assert_called_with(task_dict)


async def test_dispatcher_publish_calls_broker(
    mocker: MockerFixture,
    dispatcher: Dispatcher,
    json_serializer: JsonSerializer,
    task: Task,
) -> None:
    task_dict = task.as_dict()
    serialized_task = json_serializer.dumps(task_dict)

    patched = mocker.patch.object(dispatcher.broker, "publish")
    await dispatcher.publish(task)

    patched.assert_called_with(str(task.route), serialized_task)


async def test_dispatcher_subscribe_calls_broker(
    mocker: MockerFixture,
    dispatcher: Dispatcher,
    json_serializer: JsonSerializer,
    task: Task,
) -> None:
    task_dict = task.as_dict()
    serialized_task = json_serializer.dumps(task_dict)

    patched = mocker.patch.object(dispatcher.broker, "subscribe")
    patched.return_value = DummyAsyncIterator(t for t in [serialized_task])

    async for recv_task in dispatcher.subscribe(task.route):
        assert task == recv_task
