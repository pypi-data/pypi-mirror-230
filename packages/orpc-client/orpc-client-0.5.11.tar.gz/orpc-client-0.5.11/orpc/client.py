__all__ = [
    "OrpcClient",
    "OrpcClientPool",
]

import socket

from zenutils import hashutils
import pooling

from .protocol import DEFAULT_ORPC_PORT
from .protocol import OrpcProtocolWriter
from .protocol import OrpcProtocolReader
from .exceptions import ClientLoginFailed


class OrpcClient(object):
    def __init__(
        self,
        host="localhost",
        port=DEFAULT_ORPC_PORT,
        username=None,
        password=None,
        login_path="auth.login",
        ping_path="debug.ping",
        buffer_size=4096,
        rfile_buffer_size=None,
        wfile_buffer_size=None,
        auto_connect=True,
        auto_login=True,
        **kwargs,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.login_path = login_path
        self.ping_path = ping_path
        self.buffer_size = buffer_size
        self.rfile_buffer_size = rfile_buffer_size or self.buffer_size
        self.wfile_buffer_size = wfile_buffer_size or self.buffer_size
        self.auto_connect = auto_connect
        self.auto_login = auto_login

        if auto_connect:
            self.reconnect()

    def reconnect(self):
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        self.rfile = self.sock.makefile("rb", buffering=self.rfile_buffer_size)
        self.protocol_reader = OrpcProtocolReader(self.rfile)
        self.wfile = self.sock.makefile("wb", buffering=self.wfile_buffer_size)
        self.protocol_writer = OrpcProtocolWriter(self.wfile)

        if self.auto_login:
            if not self.login():
                raise ClientLoginFailed()

    def get_response(
        self, path, headers=None, args=None, kwargs=None, body=None, files=None
    ):
        self.protocol_writer.write_request(path, headers, args, kwargs, body, files)
        response = self.protocol_reader.read_response()
        return response

    def execute(
        self, path, headers=None, args=None, kwargs=None, body=None, files=None
    ):
        response = self.get_response(path, headers, args, kwargs, body, files)
        if response.code == 0:
            return response.result
        else:
            raise Exception(response.code, response.message)

    def login(self):
        return self.execute(
            self.login_path,
            kwargs={
                "username": self.username,
                "password": hashutils.get_password_hash(self.password),
            },
        )

    def ping(self):
        return self.execute(self.ping_path)


class OrpcClientPool(pooling.PoolBase):
    orpc_client_class = OrpcClient

    def do_session_create(self, *create_args, **create_kwargs):
        return self.orpc_client_class(*create_args, **create_kwargs)

    def get_response(
        self, path, headers=None, args=None, kwargs=None, body=None, files=None
    ):
        with self.get_session() as session:
            return session.get_response(path, headers, args, kwargs, body, files)

    def execute(
        self, path, headers=None, args=None, kwargs=None, body=None, files=None
    ):
        with self.get_session() as session:
            return session.execute(path, headers, args, kwargs, body, files)
