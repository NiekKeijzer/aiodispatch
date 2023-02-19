import asyncio
import collections
from collections.abc import AsyncGenerator
from typing import Optional, final

from .abc import Broker


@final
class MemoryBroker(Broker):
    def __init__(self, maxsize: int = 0):
        self.queues: dict[str, asyncio.Queue[bytes]] = collections.defaultdict(
            lambda: asyncio.Queue(maxsize)
        )

    async def publish(
        self, key: str, payload: bytes, timeout: Optional[float] = None
    ) -> None:
        await self.queues[key].put(payload)

    async def subscribe(self, key: str) -> AsyncGenerator[bytes, None]:
        queue = self.queues[key]
        while True:
            payload = await queue.get()
            yield payload

            queue.task_done()
