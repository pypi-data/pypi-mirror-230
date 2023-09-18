import random

import grpc

from threading import Lock
from typing import Any
from utils.errno import OK


class GrpcClientCache:
    def __init__(self, stub):
        self._lock = Lock()
        self._clis: dict[str, Any] = {}
        self._stub = stub

    def _init_cli(self, address):
        cli = self._clis.get(address)
        if cli:
            return cli
        with self._lock:
            cli = self._clis.get(address)
            if cli:
                return cli
            cli = self._stub(grpc.insecure_channel(address))
            self._clis[address] = cli
        return cli


class ServiceClient(GrpcClientCache):
    """
    使用ip port直接调用，无限流
    """
    def __init__(self, stub, ip_ports: tuple[tuple[str, str]]):
        super().__init__(stub)
        if not ip_ports:
            raise Exception("ServiceClient need ip_ports")
        self._ip_ports = ip_ports

    def _get_cli(self, tags: dict[str, set] = None):
        ip, port = random.choice(self._ip_ports)
        cli = self._init_cli(f"{ip}:{port}")
        return cli

    def do_request(self, req, method):
        cli = self._get_cli()
        # TODO: timeout stop worker
        # TODO: trans code, message to err
        res = getattr(cli, method)(req, timeout=1000)
        return res, OK
