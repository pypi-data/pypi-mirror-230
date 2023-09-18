from typing import Any

import registry_pb2_grpc as pb_grpc
from gservices import registry_pb2 as pb
from gservices.cli import ServiceClient as _ServiceClient, GrpcClientCache
from gservices.errno import NO_INSTANCE
from gservices.registry_config import RegistryConfig, Service
from utils.data import str_to_int
from utils.errno import Error, OK
from utils.flow_limit import FLockBase
from utils.log import logger
from utils.server import Context


class _RegistryCli(_ServiceClient):
    def __init__(self):
        super().__init__(pb_grpc.RegistryServiceStub, (("", ""),))

    def _get_cli(self, tags: dict[str, set] = None):
        ip, port = RegistryConfig.client_address
        cli = self._init_cli(f"{ip}:{port}")
        return cli

    def get_instance(self, service_name: str, tags: dict[str, set]) -> tuple[set[Service], Error]:
        req = pb.InstancesReq(service_name=service_name)
        for name, values in tags.items():
            req.tags.append(pb.Tag(name=name, values=list(values)))
        res, err = self.do_request(req, "Instances")
        if not err.ok:
            return set(), err
        services = set()
        for instance in res.instances:
            services.add(Service(ip=instance.ip, port=instance.port))
        return services, OK


RegistryCli = _RegistryCli()


class FConLimit(FLockBase):
    def _con_limit(self) -> int:
        return RegistryConfig.concurrency

    def _key_prefix(self):
        return "registry"


class ServiceClient(GrpcClientCache):
    def __init__(self, stub, service_name, flow_limit=None):
        super().__init__(stub)
        if not service_name:
            raise Exception("ServiceClient need registry service_name")
        self._service_name = service_name
        if flow_limit is None:
            self._flow_limit = FConLimit()
        self._registry_cli = RegistryCli

    def _filter_service(self, _id: str, tags: dict[str, set] = None) -> tuple[Service, Error]:
        if tags is None:
            tags = {}
        services, err = self._registry_cli.get_instance(self._service_name, tags)
        if not err.ok:
            return Service("", ""), err
        if not services:
            return Service("", ""), NO_INSTANCE
        services = list(services)
        services.sort()
        i = str_to_int(_id) % len(services)
        service = services[i]
        return service, OK

    def do_request(self, task_id, req, method, limit_flow=False,
                   tags: dict[str, set] = None) -> tuple[Any, Error]:
        service, err = self._filter_service(task_id, tags)
        if not err.ok:
            return None, err
        logger.debug(f"===ServiceClient get service {tags} {service}")
        cli = self._init_cli(f"{service.ip}:{service.port}")
        if not limit_flow:
            res = getattr(cli, method)(req, timeout=30 * 60)
            return res, OK

        # 目前一台机器算力有限，不能分接口限流；method参数其实没用
        with self._flow_limit.ing(Context(30), f"{service.ip}={service.port}", "default_client") as err:
            if not err.ok:
                return None, err
            # TODO: timeout stop worker
            res = getattr(cli, method)(req, timeout=30 * 60)
            # TODO: trans code, message to err
            return res, OK
