import traceback
from google.protobuf.json_format import MessageToDict
from functools import wraps
from utils.errno import INTERVAL_SERVER
from gservices.utils import trans_ret, trans_ret_code
from utils.auth.token import get_user
from utils.log import logger


def catch_decorator(ret_class):
    """
    捕获异常
    :param ret_class:
    :return:
    """

    def _decorator(func):
        @wraps(func)
        def decorated(self, req, context):
            req_p = req
            try:
                req_p = MessageToDict(
                    req, including_default_value_fields=True,
                    preserving_proto_field_name=True, use_integers_for_enums=True)
            except AttributeError:
                pass

            try:
                logger.info(f"execute {func.__name__} req={req_p}")
                res = func(self, req, context)
                logger.debug(f"execute {func.__name__} req={req_p} res={res}")
                return res
            except Exception as e:
                logger.error(f"{func.__name__} raise err={e} \n {traceback.format_exc()}")
                return trans_ret(ret_class, INTERVAL_SERVER)

        return decorated

    return _decorator


def verify_user_decorator(ret_class, need_code: bool = True, check_code=False):
    """
    token校验
    :param ret_class:
    :param need_code:
    :param check_code:
    :return:
    """

    def _decorator(func):
        """
        校验token是否正常
        """

        @wraps(func)
        def decorated(self, req, context):
            # TODO: call user service
            user, err = get_user(req.token)
            if err.ok:
                return func(self, user, req, context)
            logger.error(f"verify_user_decorator {err}")
            if need_code:
                if check_code:
                    return trans_ret(ret_class, err)
                else:
                    return trans_ret_code(ret_class, err)
            else:
                return ret_class()

        return decorated

    return _decorator
