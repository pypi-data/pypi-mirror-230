__all__ = [
    "OrpcFile",
    "OrpcRequest",
    "OrpcResponse",
    "OrpcProtocolWriter",
    "OrpcProtocolReader",
]

import json
import msg2bytes


DEFAULT_ORPC_PORT = 2801


class OrpcFile(msg2bytes.File):
    """ORPC附件"""

    @classmethod
    def from_msg2bytes_file(cls, x):
        y = cls()
        y.root = x.root
        y.filename = x.filename
        y.filepath = x.filepath
        return y


msg2bytes.register_dump_codec(msg2bytes.FileCodec, OrpcFile)


class OrpcRequest(object):
    """ORPC请求。"""

    def __init__(self):
        self.path = ""
        self.headers = {}
        self.args = []
        self.kwargs = {}
        self.body = ""
        self.files = []

    def __repr__(self):
        return json.dumps(
            {
                "path": self.path,
                "headers": self.headers,
                "args": self.args,
                "kwargs": self.kwargs,
                "body": self.body,
                "files": self.files,
            },
            ensure_ascii=False,
        )


class OrpcResponse(object):
    """ORPC响应."""

    def __init__(self):
        self.code = 0
        self.headers = {}
        self.message = "OK"
        self.result = None
        self.files = []

    def __repr__(self) -> str:
        return json.dumps(
            {
                "code": self.code,
                "headers": self.headers,
                "message": self.message,
                "result": self.result,
                "files": self.files,
            },
            ensure_ascii=False,
        )


class OrpcProtocolWriter(object):
    def __init__(self, wfile, **kwargs):
        self.wfile = wfile
        self.kwargs = kwargs

    def write_request(
        self, path, headers=None, args=None, kwargs=None, body="", files=None
    ):
        headers = headers or {}
        args = args or ()
        kwargs = kwargs or {}
        files = files or []
        msg2bytes.dump(path, self.wfile, **self.kwargs)
        msg2bytes.dump(headers, self.wfile, **self.kwargs)
        msg2bytes.dump(args, self.wfile, **self.kwargs)
        msg2bytes.dump(kwargs, self.wfile, **self.kwargs)
        msg2bytes.dump(body, self.wfile, **self.kwargs)
        msg2bytes.dump(files, self.wfile, **self.kwargs)
        self.wfile.flush()

    def write_response(
        self, code=0, headers=None, message="OK", result=None, files=None
    ):
        headers = headers or {}
        files = files or []
        msg2bytes.dump(code, self.wfile, **self.kwargs)
        msg2bytes.dump(headers, self.wfile, **self.kwargs)
        msg2bytes.dump(message, self.wfile, **self.kwargs)
        msg2bytes.dump(result, self.wfile, **self.kwargs)
        msg2bytes.dump(files, self.wfile, **self.kwargs)
        self.wfile.flush()

    async def async_write_request(
        self, path, headers=None, args=None, kwargs=None, body="", files=None
    ):
        headers = headers or {}
        args = args or ()
        kwargs = kwargs or {}
        files = files or []
        await msg2bytes.async_dump(path, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(headers, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(args, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(kwargs, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(body, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(files, self.wfile, **self.kwargs)
        await self.wfile.flush()

    async def async_write_response(
        self, code=0, headers=None, message="OK", result=None, files=None
    ):
        headers = headers or {}
        files = files or []
        await msg2bytes.async_dump(code, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(headers, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(message, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(result, self.wfile, **self.kwargs)
        await msg2bytes.async_dump(files, self.wfile, **self.kwargs)
        await self.wfile.flush()


class OrpcProtocolReader(object):
    def __init__(self, rfile, **kwargs):
        self.rfile = rfile
        self.kwargs = kwargs

    def read_request(self):
        request = OrpcRequest()
        request.path = msg2bytes.load(self.rfile, **self.kwargs)
        request.headers = msg2bytes.load(self.rfile, **self.kwargs)
        request.args = msg2bytes.load(self.rfile, **self.kwargs)
        request.kwargs = msg2bytes.load(self.rfile, **self.kwargs)
        request.body = msg2bytes.load(self.rfile, **self.kwargs)
        request.files = [
            OrpcFile.from_msg2bytes_file(x)
            for x in msg2bytes.load(self.rfile, **self.kwargs)
        ]
        return request

    def read_response(self):
        response = OrpcResponse()
        response.code = msg2bytes.load(self.rfile, **self.kwargs)
        response.headers = msg2bytes.load(self.rfile, **self.kwargs)
        response.message = msg2bytes.load(self.rfile, **self.kwargs)
        response.result = msg2bytes.load(self.rfile, **self.kwargs)
        response.files = [
            OrpcFile.from_msg2bytes_file(x)
            for x in msg2bytes.load(self.rfile, **self.kwargs)
        ]
        return response

    async def async_read_request(self):
        request = OrpcRequest()
        request.path = await msg2bytes.async_load(self.rfile, **self.kwargs)
        request.headers = await msg2bytes.async_load(self.rfile, **self.kwargs)
        request.args = await msg2bytes.async_load(self.rfile, **self.kwargs)
        request.kwargs = await msg2bytes.async_load(self.rfile, **self.kwargs)
        request.body = await msg2bytes.async_load(self.rfile, **self.kwargs)
        request.files = [
            OrpcFile.from_msg2bytes_file(x)
            for x in await msg2bytes.async_load(self.rfile, **self.kwargs)
        ]
        return request

    async def async_read_response(self):
        response = OrpcResponse()
        response.code = await msg2bytes.async_load(self.rfile, **self.kwargs)
        response.headers = await msg2bytes.async_load(self.rfile, **self.kwargs)
        response.message = await msg2bytes.async_load(self.rfile, **self.kwargs)
        response.result = await msg2bytes.async_load(self.rfile, **self.kwargs)
        response.files = [
            OrpcFile.from_msg2bytes_file(x)
            for x in await msg2bytes.async_load(self.rfile, **self.kwargs)
        ]
        return response
