__all__ = [
    "AsioReader",
    "AsioWriter",
]


class AsioReader(object):
    def __init__(self, reader):
        self.reader = reader

    async def read(self, size):
        return await self.reader.readexactly(size)


class AsioWriter(object):
    def __init__(self, writer, buffering=4096):
        self.writer = writer
        self.counter = 0
        self.buffering = buffering

    async def write(self, data):
        self.counter += len(data)
        self.writer.write(data)
        if self.counter > self.buffering:
            await self.flush()

    async def flush(self):
        await self.writer.drain()
        self.counter = 0
