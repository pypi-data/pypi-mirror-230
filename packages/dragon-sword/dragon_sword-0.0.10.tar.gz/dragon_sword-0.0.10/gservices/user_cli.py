from threading import Lock

import grpc

import user_pb2 as pb
from gservices.utils import check_code
from registry_cli import RegistryCli
from user_pb2_grpc import UserServiceStub
from utils.config import user_service_name
from utils.errno import Error, OK
from utils.log import logger


class _UserCli:
    def __init__(self, service_name):
        self._lock = Lock()
        self._service_name = service_name
        self._clis = {}
        self._registry_cli = RegistryCli

    def _get_cli_from_cache(self, address: str):
        return self._clis.get(address)

    def _get_cli(self) -> tuple[UserServiceStub, Error]:
        ip, port, err = self._registry_cli.get_instance(self._service_name)
        if not err.ok:
            logger.error(f"UserCli get registry err {err}")
            return None, err

        _address = f"{ip}:{port}"
        cli = self._get_cli_from_cache(_address)
        if not cli:
            with self._lock:
                cli = self._get_cli_from_cache(_address)
                if cli:
                    return cli, OK
                cli = UserServiceStub(grpc.insecure_channel(_address))
                self._clis[_address] = cli
        return cli, OK

    def signup(self, user: str, passwd: str, mode: str) -> tuple[str, Error]:
        cli, err = self._get_cli()
        if not err.ok:
            return "", err

        req = pb.SignupReq(user=user, passwd=passwd, mode=mode)
        res = cli.Signup(req)

        err = check_code(res)
        if not err.ok:
            return "", err
        return res.token, OK

    def verify_user(self, token: str) -> tuple[str, Error]:
        cli, err = self._get_cli()
        if not err.ok:
            return "", err

        req = pb.VerifyUserReq(token=token)
        res = cli.VerifyUser(req)

        err = check_code(res)
        if not err.ok:
            return "", err
        return res.user, OK


UserCli = _UserCli(user_service_name())
