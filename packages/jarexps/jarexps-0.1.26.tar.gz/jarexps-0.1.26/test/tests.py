import os
import unittest
from orpc.client import OrpcClientPool


class TestJarexps(unittest.TestCase):
    def setUp(self):
        self.cp = OrpcClientPool(
            10,
            kwargs={
                "host": "localhost",
                "port": 3182,
                "username": "HNVL0uqb",
                "password": "O6TIl6D2enfluEtren7YginEKWUF1Rtm",
            },
        )

    def test1(self):
        data1 = b"hello world"
        data2 = self.cp.execute("misc.base64.encode", args=[data1])
        assert data2 == b"aGVsbG8gd29ybGQ="

    def test2(self):
        data1 = os.urandom(1024)
        data2 = self.cp.execute("misc.base64.encode", args=[data1])
        data3 = self.cp.execute("misc.base64.decode", args=[data2])
        assert data1 == data3
