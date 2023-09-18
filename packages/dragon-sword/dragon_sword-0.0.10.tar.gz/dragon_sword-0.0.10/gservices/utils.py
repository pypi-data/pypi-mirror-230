from utils.errno import Error, THIRD_SERVER, OK
from utils.log import logger


def trans_ret(ret_class, err: Error):
    return ret_class(check_code=err.code, check_desc=err.desc)


def trans_ret_code(ret_class, err: Error, doc=None):
    ret = ret_class(code=err.code, message=err.desc)
    if doc:
        ret.doc = doc
    return ret


def check_code(res) -> Error:
    if res.code != "":
        logger.error(f"{res}")
        return THIRD_SERVER
    return OK
