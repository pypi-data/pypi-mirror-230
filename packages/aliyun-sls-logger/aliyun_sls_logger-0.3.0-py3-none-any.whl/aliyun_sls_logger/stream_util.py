import asyncio
from contextlib import asynccontextmanager

from aiostream import operator, pipe, streamcontext


@asynccontextmanager
async def buffer(streamer, size=1):
    queue = asyncio.Queue(maxsize=size)
    sentinel = object()

    async def consume():
        try:
            async for item in streamer:
                await queue.put(item)
        finally:
            await queue.put(sentinel)

    @operator
    async def wrapper():
        while True:
            item = await queue.get()
            queue.task_done()
            if item is sentinel:
                await future
                return
            yield item

    future = asyncio.ensure_future(consume())
    try:
        yield wrapper()
    finally:
        future.cancel()


@operator(pipable=True)
async def catch(source, exc_cls):
    async with streamcontext(source) as streamer:
        try:
            async for item in streamer:
                yield item
        except exc_cls:
            return


@operator(pipable=True)
async def buffer_timeout(source, n, timeout):
    async with streamcontext(source) as streamer:
        async with buffer(streamer) as buffered:
            async with streamcontext(buffered) as first_streamer:
                async for first in first_streamer:
                    tail = await (
                            buffered
                            | pipe.timeout(timeout)
                            | catch.pipe(asyncio.TimeoutError)
                            | pipe.take(n - 1)
                            | pipe.list()
                    )
                    yield [first, *tail]
