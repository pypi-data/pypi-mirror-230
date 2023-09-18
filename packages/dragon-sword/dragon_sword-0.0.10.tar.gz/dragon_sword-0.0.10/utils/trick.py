from functools import wraps
from utils.log import logger


def switch_enable(*default_ret):
    """
    如果类enable=False，则直接返回默认
    :param default_ret: 默认返回数据
    :return:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not getattr(self, "enable", False):
                logger.debug(f"{func.__name__} do nothing")
                return default_ret
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
