from utils.errno import OK
from gservices import user_pb2 as pb, user_pb2_grpc as pb_grpc
from gservices.decorator import catch_decorator
from gservices.utils import trans_ret_code
from utils.log import logger


class UserService(pb_grpc.UserServiceServicer):
    """
    用户服务
    """

    def __init__(self, doc, signup, verify_user, access):
        self._doc = doc
        self._signup = signup
        self._verify_user = verify_user
        self._access = access
        super().__init__()

    @catch_decorator(pb.SignupRes)
    def Signup(self, req: pb.SignupReq, context) -> pb.SignupRes:
        """
        用户登录
        :param req:
        :param context:
        :return:
        """
        # TODO: 根据mode，通过不同校验，token里加上mode
        token, err = self._signup(req.user, req.passwd)
        if not err.ok:
            logger.error(f"Signup {req} {err}")
        ret = trans_ret_code(pb.SignupRes, err, doc=self._doc)
        ret.token = token
        return ret

    @catch_decorator(pb.VerifyUserRes)
    def VerifyUser(self, req: pb.VerifyUserReq, context) -> pb.VerifyUserRes:
        """
        校验用户
        :param req:
        :param context:
        :return:
        """
        user, err = self._verify_user(req.token)
        if not err.ok:
            logger.error(f"VerifyUser {req} {err}")
        ret = trans_ret_code(pb.VerifyUserRes, err, doc=self._doc)
        ret.user = user
        return ret

    @catch_decorator(pb.AccessRes)
    def Access(self, req: pb.AccessReq, context) -> pb.AccessRes:
        # TODO: 完善逻辑
        ret = trans_ret_code(pb.AccessRes, OK, doc=self._doc)
        for item in self._access():
            ret.projects.append(item)
        return ret
