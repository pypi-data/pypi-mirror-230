from collections import defaultdict
from dataclasses import dataclass

from utils.config import get_conf, get_default
from utils.server_config import CommonConf
from utils.data import Cache, LowStr
from utils.log import logger


@dataclass
class FlowLimit:
    concurrency: int


@dataclass(frozen=True, eq=True, order=True)
class Service:
    ip: str
    port: str


class Tag(LowStr):
    pass


class TagField(LowStr):
    pass


class _RegistryConfig(Cache):
    def __init__(self):
        super().__init__()
        self._name = "registry"

        self._service_flow_limit: FlowLimit
        self._client_address: tuple[str, str]
        self._name_server: dict[str, list[Service]]
        self._tag_server: dict[TagField, dict[Tag, set[Service]]]
        self._common_server: set[Service]

    def _load_server(self, conf):
        # 注册服务端
        _flow = get_default(conf, "flow_limit", {})
        self._service_flow_limit = FlowLimit(concurrency=get_default(_flow, "concurrency", 1))

        self._tag_server = {}
        self._common_server = set()
        self._name_server = defaultdict(list)
        # 初始化服务器名，暂时不用
        service_name = get_default(conf, "service_name", {})
        for name, services in service_name.items():
            for ip_port in services:
                ip, port = ip_port.split(":")
                self._name_server[name].append(Service(ip=ip, port=port))

        # 初始化服务器tag
        service_tag = get_default(conf, "service_tag", {
            # 默认本机支持所有能力
            f"{CommonConf.ID}:{CommonConf.port}": {}
        })
        for ip_port, tags in service_tag.items():
            logger.debug(f"{ip_port} {tags}")
            ip, port = ip_port.split(":")
            _service = Service(ip=ip, port=port)
            if not tags:
                self._common_server.add(_service)
                continue
            for tag_field, tag_values in tags.items():
                _field = TagField(tag_field)
                if _field not in self._tag_server:
                    self._tag_server[_field] = defaultdict(set)
                for tag_value in tag_values:
                    self._tag_server[_field][Tag(tag_value)].add(Service(ip, port))

    def _load_client(self, conf):
        # 客户端
        address = get_default(conf, "address", {"ip": CommonConf.ID, "port": CommonConf.port})
        self._client_address = (address["ip"], address["port"])

    def _load(self):
        conf = get_conf(self._name)
        server = get_default(conf, "server", {})
        self._load_server(server)
        client = get_default(conf, "client", {})
        self._load_client(client)

    def is_service(self):
        return self._get("_service_flow_limit") is not None

    def is_client(self):
        return self.client_address is not None

    @property
    def client_address(self):
        return self.get("_client_address")

    @property
    def concurrency(self) -> int:
        return self.get("_service_flow_limit").concurrency

    @property
    def tag_server(self) -> dict[TagField, dict[Tag, set[Service]]]:
        return self.get("_tag_server")

    @property
    def common_server(self) -> set[Service]:
        return self.get("_common_server")

    def filter_server(self, tags: dict[str, set]) -> set[Service]:
        """
        :param tags: 需要满足的tag
        :return:
        """
        result = set()
        for tag, values in tags.items():
            if result is None:
                break
            source = self.tag_server.get(TagField(tag))
            if not source:
                # 如cooker_name，客户端使用的tag项，服务端没有该tag项（下面无任何机器），忽略该tag限制
                logger.debug(f"_RegistryCli filter_ip_port no tag {tag}, ignore")
                continue

            # 服务端有对应tag项，检查value限制
            for value in values:
                addresses = source.get(Tag(value))
                # 该限制tag下，无任何机器；RegistryConfig.tag_server有限制的机器，肯定无法满足
                if not addresses:
                    result = None
                    break

                if not result:
                    result = addresses
                result = result & addresses

        if result is None:
            result = set()
        result.update(RegistryConfig.common_server)
        logger.debug(f"filter_ip_port {tags} {RegistryConfig.common_server} {RegistryConfig.tag_server} {result}")
        return result


RegistryConfig = _RegistryConfig()
