import contextvars
import dataclasses
from collections.abc import AsyncGenerator
from typing import Final

from .brokers.abc import Broker
from .enums import Route
from .serializers.abc import Serializer
from .tasks import Task

dispatcher: Final[contextvars.ContextVar["Dispatcher"]] = contextvars.ContextVar(
    "dispatcher"
)


@dataclasses.dataclass
class Dispatcher:
    broker: Broker
    serializer: Serializer

    def __post_init__(self) -> None:
        dispatcher.set(self)

    async def publish(self, task: Task) -> None:
        raw = self.serializer.dumps(task.as_dict())
        await self.broker.publish(str(task.route), raw)

    async def subscribe(self, route: Route = Route.TASKS) -> AsyncGenerator[Task, None]:
        async for raw in self.broker.subscribe(str(route)):
            payload = self.serializer.loads(raw)
            task = Task.from_dict(payload)

            yield task
