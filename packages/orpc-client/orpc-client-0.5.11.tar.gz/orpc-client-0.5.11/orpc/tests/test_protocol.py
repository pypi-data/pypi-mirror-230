from fileinput import filename
import io
import os
import unittest
from orpc.protocol import OrpcProtocolReader
from orpc.protocol import OrpcProtocolWriter
from orpc.protocol import OrpcFile


class TestProtocol(unittest.TestCase):
    def test1(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_request("ping")
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        request = reader.read_request()
        assert request.path == "ping"

    def test2(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_request("echo", args=["hello world"])
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        request = reader.read_request()
        assert request.path == "echo"
        assert request.args[0] == "hello world"

    def test3(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_request("echo", kwargs={"msg": "hello world"})
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        request = reader.read_request()
        assert request.path == "echo"
        assert request.kwargs["msg"] == "hello world"

    def test4(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_response(result="pong")
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        response = reader.read_response()
        assert response.code == 0
        assert response.message == "OK"
        assert response.result == "pong"

    def test5(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_response(result=None)
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        response = reader.read_response()
        assert response.code == 0
        assert response.message == "OK"
        assert response.result == None

    def test6(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_response(result=True)
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        response = reader.read_response()
        assert response.code == 0
        assert response.message == "OK"
        assert response.result == True

    def test7(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_response(result=False)
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        response = reader.read_response()
        assert response.code == 0
        assert response.message == "OK"
        assert response.result == False

    def test8(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_response(result=[1, 2, 3])
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        response = reader.read_response()
        assert response.code == 0
        assert response.message == "OK"
        assert response.result == [1, 2, 3]

    def test9(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_response(result=set([1, 2, 3]))
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        response = reader.read_response()
        assert response.code == 0
        assert response.message == "OK"
        assert response.result == set([1, 2, 3])

    def test10(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_response(result=tuple([1, 2, 3]))
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        response = reader.read_response()
        assert response.code == 0
        assert response.message == "OK"
        assert response.result == tuple([1, 2, 3])

    def test11(self):
        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_request(
            "ping", headers={"App-Auth": "dR9gBUDhOxZrSFkC0KsLKihm2evabJ21"}
        )
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        request = reader.read_request()
        assert request.path == "ping"
        assert request.headers["App-Auth"] == "dR9gBUDhOxZrSFkC0KsLKihm2evabJ21"

    def test12(self):
        data1 = os.urandom(1024)
        file1 = OrpcFile()
        with open(file1.filepath, "wb") as fobj:
            fobj.write(data1)

        buf = io.BytesIO()
        writer = OrpcProtocolWriter(buf)
        writer.write_request(
            "ping",
            headers={"App-Auth": "dR9gBUDhOxZrSFkC0KsLKihm2evabJ21"},
            files=[file1],
        )
        buf.seek(0)
        reader = OrpcProtocolReader(buf)
        request = reader.read_request()
        assert request.path == "ping"
        assert request.headers["App-Auth"] == "dR9gBUDhOxZrSFkC0KsLKihm2evabJ21"
        assert request.files[0].filename == file1.filename
        assert request.files[0].filesize == file1.filesize
        assert request.files[0].filepath != file1.filepath

        with open(file1.filepath, "rb") as fobj:
            f1content = fobj.read()
        with open(request.files[0].filepath, "rb") as fobj:
            f2content = fobj.read()
        assert f1content == f2content

        os.unlink(file1.filepath)
        os.unlink(request.files[0].filepath)
