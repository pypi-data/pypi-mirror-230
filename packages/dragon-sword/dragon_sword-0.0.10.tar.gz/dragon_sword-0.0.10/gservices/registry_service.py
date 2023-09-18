import registry_pb2 as pb
import registry_pb2_grpc as pb_grpc
from gservices.decorator import catch_decorator
from gservices.registry_config import Service, RegistryConfig
from gservices.utils import trans_ret_code
from utils.errno import OK
from utils.log import logger

# 可在接口附加迁移通知
_doc = "latest"


class RegistryService(pb_grpc.RegistryServiceServicer):
    @catch_decorator(pb.RegisterRes)
    def Register(self, req: pb.RegisterReq, context) -> pb.RegisterRes:
        ret = trans_ret_code(pb.RegisterRes, OK, doc=_doc)
        return ret

    @catch_decorator(pb.InstancesRes)
    def Instances(self, req: pb.InstancesReq, context) -> pb.InstancesRes:
        # 名字服务，暂时不用，烘焙用到的目前需要是一个worker机器
        # TODO：机器变更时，负载到不同机器上，进行任务重试
        service_name = req.service_name
        _tags = req.tags
        tags = {}
        for tag in _tags:
            tags[tag.name] = set(tag.values)
        services = RegistryConfig.filter_server(tags)

        ret = trans_ret_code(pb.InstancesRes, OK, doc=_doc)
        for service in services:
            ret.instances.append(pb.Instance(ip=service.ip, port=service.port))
        return ret
