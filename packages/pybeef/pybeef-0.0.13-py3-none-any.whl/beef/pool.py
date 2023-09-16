import contextlib
import asyncio
import aio_pika
from typing import List


class Pool:

    def __init__(self, connection: aio_pika.abc.AbstractRobustConnection, max_items=10):
        self._connection = connection
        self._idle = asyncio.Queue()
        self._channels: List[aio_pika.abc.AbstractRobustChannel] = []
        self.max_items = max_items
        self._closed = False

    @contextlib.asynccontextmanager
    async def acquire(self) -> aio_pika.abc.AbstractRobustChannel:
        if self._closed:
            raise RuntimeError('Pool is closed')
        try:
            while True:
                channel = self._idle.get_nowait()
                if channel.is_closed:
                    continue
                try:
                    yield channel
                finally:
                    self._idle.put_nowait(channel)
                return
        except asyncio.QueueEmpty:
            pass

        self._channels = [c for c in self._channels if not c.is_closed]
        if len(self._channels) >= self.max_items:
            channel = await self._idle.get()
            try:
                yield channel
            finally:
                self._idle.put_nowait(channel)
            return

        channel = await self._connection.channel()
        self._channels.append(channel)
        try:
            yield channel
        finally:
            self._idle.put_nowait(channel)

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True

        tasks = [asyncio.create_task(c.close()) for c in self._channels]
        self._channels = []
        await asyncio.gather(*tasks, return_exceptions=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()