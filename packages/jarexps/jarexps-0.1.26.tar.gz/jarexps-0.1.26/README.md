# jarexps

Setup a simple Open RPC server to export services from a jar file.

## Install

```
pip install jarexps
```

## Usage

*Example config.yml*

```
daemon: true
loglevel: INFO

server:
  listen: 0.0.0.0
  port: 1813

authentication:
  enable: true
  users:
    app01: sNKBMFEol0w8CWUCkgxpxlhzbHeHx264

jarexps:
  classpaths:
    - abs/path/to/bcprov-jdk15on-1.70.jar
  services:
    misc.base64.encode:
      klass: org.bouncycastle.util.encoders.Base64
      method: encode
    misc.base64.decode:
      klass: org.bouncycastle.util.encoders.Base64
      method: decode

orpc:
  handler:
    asio-writer-buffer-size: 4096
```

*start server command*

```
jarexpsd -c config.yml start
```

*client tests*

```
import os
import unittest
from orpc.client import OrpcClientPool


class TestJarexps(unittest.TestCase):
    def setUp(self):
        self.cp = OrpcClientPool(
            10,
            kwargs={
                "host": "localhost",
                "port": 1813,
                "username": "app01",
                "password": "sNKBMFEol0w8CWUCkgxpxlhzbHeHx264",
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
```

## Releases

### v0.1.25

- First release.

### v0.1.26

- Doc update.
