import asyncio
import dataclasses
import os
import signal
from collections.abc import AsyncIterable
from typing import ClassVar

from .dispatch import Dispatcher
from .enums import Route
from .exceptions import AlreadyStoppingException
from .tasks import Task


@dataclasses.dataclass(frozen=True)
class Worker:
    SIGNALS: ClassVar[list[int]] = (
        [signal.SIGINT, signal.SIGTERM] if os.name != "nt" else [signal.SIGTERM]
    )

    dispatcher: Dispatcher
    semaphore: asyncio.Semaphore = dataclasses.field(
        default_factory=asyncio.BoundedSemaphore
    )

    _event: asyncio.Event = dataclasses.field(init=False, default_factory=asyncio.Event)
    _task_group: asyncio.TaskGroup = dataclasses.field(
        init=False, default_factory=asyncio.TaskGroup
    )
    _pending_tasks: set[asyncio.Task] = dataclasses.field(
        init=False, default_factory=set
    )

    @property
    def pending_count(self) -> int:
        return len(self._pending_tasks)

    async def start(self, route: Route = Route.TASKS) -> None:
        self.register_signals()

        tasks = self.dispatcher.subscribe(route)
        process = asyncio.create_task(self._process(tasks))
        self._pending_tasks.add(process)

        await self._event.wait()

    def stop(self) -> None:
        if self.is_stopping():
            raise AlreadyStoppingException()

        self._event.set()

        for aiotask in self._pending_tasks:
            aiotask.cancel()

        self.cleanup_signals()

    def register_signals(self):
        loop = asyncio.get_running_loop()
        for sig in self.SIGNALS:
            loop.add_signal_handler(sig, self.stop)

    def cleanup_signals(self):
        loop = asyncio.get_running_loop()
        for sig in self.SIGNALS:
            loop.remove_signal_handler(sig)

    def is_stopping(self) -> bool:
        return self._event.is_set()

    async def _process(self, tasks: AsyncIterable[Task]) -> None:
        async with self._task_group as tg:
            async for task in tasks:
                aio_task = tg.create_task(self._run_task(task))
                aio_task.add_done_callback(lambda t: self._pending_tasks.discard(t))

                self._pending_tasks.add(aio_task)

    async def _run_task(self, task: Task) -> None:
        async with self.semaphore:
            await task()
