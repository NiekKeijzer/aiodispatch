import asyncio
import signal

import pytest
from pytest_mock import MockerFixture

from aiotasq.dispatch import Dispatcher
from aiotasq.exceptions import AlreadyStoppingException
from aiotasq.tasks import Task
from aiotasq.worker import Worker

from .utils import DummyAsyncIterator


@pytest.fixture()
def unstarted_worker(dispatcher: Dispatcher) -> Worker:
    return Worker(dispatcher=dispatcher)


async def test_signal_handlers_registered(
    mocker: MockerFixture,
    dispatcher: Dispatcher,
    event_loop: asyncio.events.AbstractEventLoop,
) -> None:
    worker = Worker(dispatcher)
    patched = mocker.patch.object(event_loop, "add_signal_handler")

    worker.register_signals()

    patched.assert_has_calls(
        [
            mocker.call(signal.SIGINT, worker.stop),
            mocker.call(signal.SIGTERM, worker.stop),
        ]
    )


async def test_stop_worker_removes_signal_handlers(
    mocker: MockerFixture, event_loop: asyncio.events.AbstractEventLoop, worker: Worker
) -> None:
    patched = mocker.patch.object(event_loop, "remove_signal_handler")

    worker.cleanup_signals()
    patched.assert_has_calls([mocker.call(signal.SIGINT), mocker.call(signal.SIGTERM)])


async def test_stop_worker(worker: Worker) -> None:
    assert not worker.is_stopping()

    worker.stop()
    assert worker.is_stopping()


async def test_stop_worker_twice_raises_exception(worker: Worker) -> None:
    assert not worker.is_stopping()

    worker.stop()
    with pytest.raises(AlreadyStoppingException):
        worker.stop()


async def test_worker_calls_tasks_in_iterable(
    unstarted_worker: Worker, task: Task
) -> None:
    tasks = DummyAsyncIterator(
        iter(
            [
                task,
            ]
        )
    )
    await unstarted_worker._process(tasks)

    assert task.is_done()


async def test_worker_calls_task(worker: Worker, task: Task) -> None:
    await worker._run_task(task)
    assert task.is_done()
