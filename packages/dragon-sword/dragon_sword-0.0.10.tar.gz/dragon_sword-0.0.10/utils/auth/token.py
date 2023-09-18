import base64
import binascii
import hmac
import time
from functools import wraps

from utils.auth.auth import AuthM
from utils.errno import (
    OK, Error,
)
from utils.auth.errno import TOKEN_EMPTY, TOKEN_EXPIRE, TOKEN_B64_DECODE, TOKEN_NOT_UTF8, TOKEN_LENGTH, TOKEN_EXPIRED, \
    TOKEN_NO_USER
from utils.time import get_now_stamp_float
from utils.log import logger


#  1. 客户端使用用户名跟密码请求登录
#  2. 服务端收到请求，去验证用户名与密码
#  3. 验证成功后，服务端会签发一个 Token，再把这个  Token 发送给客户端
#  4. 客户端收到 Token 以后可以把它存储起来，比如放在 Cookie 里或者 Local Storage 里
#  5. 客户端每次向服务端请求资源的时候需要带着服务端签发的 Token
#  6. 服务端收到请求，然后去验证客户端请求里面带着的 Token，如果验证成功，就向客户端返回请求的数据

class Token:
    _expire = 60 * 60 * 24 * 7  # 24h * 7  一周

    def __init__(self):
        self._t_str: str = None
        self._name_sha: str = None
        self._token: str = None

    @property
    def token(self) -> str:
        return self._token

    @property
    def t_str(self):
        return self._t_str

    @property
    def name_sha(self):
        return self._name_sha

    @staticmethod
    def _get_name_enc(name: str, t_str: str):
        sha1 = hmac.new(name.encode("utf-8"), t_str.encode("utf-8"), 'sha1').hexdigest()
        return sha1

    def _compare(self, name: str) -> bool:
        """
        判断name是不是token的用户名
        :param name:
        :return:
        """
        if not name:
            return False
        return self._name_sha == self._get_name_enc(name, self._t_str)

    def filter_user(self, users) -> tuple[str, Error]:
        """
        从一堆用户名中，找出和token匹配的用户名
        :param users:
        :return:
        """
        for user in users:
            if self._compare(user):
                return user, OK
        return "", TOKEN_NO_USER

    def generate(self, name: str, t: float) -> str:
        """
        根据名字和时间，生成token
        :param name:
        :param t:
        :return:
        """
        self._t_str = str(t + self._expire)
        self._name_sha = self._get_name_enc(name, self._t_str)

        token = f"{self._t_str}:{self._name_sha}"
        b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
        self._token = b64_token.decode("utf-8")
        return self._token

    def parse(self, token: str) -> tuple[str, str, Error]:
        """
        解析token，获取加密后的name和有效期时间戳
        :param token:
        :return:
        """
        self._token = token
        try:
            token_str = base64.urlsafe_b64decode(token)
        except binascii.Error:
            logger.error(f"certify_token get not base64 token {token}")
            return "", "", TOKEN_B64_DECODE
        except ValueError as e:
            logger.error(f"certify_token {e}")
            return "", "", TOKEN_B64_DECODE

        try:
            token_str = token_str.decode('utf-8')
        except UnicodeDecodeError:
            logger.error(f"certify_token get invalid byte {token}")
            return "", "", TOKEN_NOT_UTF8

        name_t = token_str.split(':')
        if len(name_t) != 2:
            return "", "", TOKEN_LENGTH

        self._t_str = name_t[0]
        self._name_sha = name_t[1]
        return self._t_str, self._name_sha, OK

    def _is_expired(self) -> bool:
        """
        token是否已过期
        :return:
        """
        return float(self._t_str) < time.time()

    def validate(self, token) -> Error:
        """
        token是否有效
        :return:
        """
        _, _, err = self.parse(token)
        if not err.ok:
            return err
        if self._is_expired():
            return TOKEN_EXPIRED
        return OK


def certify_token_decorator(ret_class, need_code: bool = True):
    """
    token校验
    :param ret_class:
    :param need_code:
    :return:
    """

    def _decorator(func):
        """
        校验token是否正常
        """

        @wraps(func)
        def decorated(self, request, context):
            token = request.token
            err = check_token(token)
            if err.ok:
                return func(self, request, context)
            logger.error(f"certify_token_decorator {err}")
            if need_code:
                return ret_class(check_code=err.code, check_desc=err.desc)
            else:
                return ret_class()

        return decorated

    return _decorator


def check_token(token) -> Error:
    if not token or len(token) == 0:
        return TOKEN_EMPTY
    if not certify_token(token):
        return TOKEN_EXPIRE
    return OK


def certify_token(token: str) -> bool:
    _, err = get_user(token)
    return err.ok


def get_user(token: str) -> tuple[str, Error]:
    """
    验证token
    :param token:
    :return: 用户名，错误码
    """
    t = Token()
    err = t.validate(token)
    if not err.ok:
        return "", err

    return t.filter_user(AuthM.all_users)


def certify_user(name, pwd) -> (str, Error):
    """
    校验用户名密码，生成token
    :param name:
    :param pwd:
    :return:
    """
    err = AuthM.check_user_passwd(name, pwd)
    if not err.ok:
        return "", err
    token = _generate_token(name)
    return token.token, OK


def _generate_token(name) -> Token:
    token = Token()
    token.generate(name, get_now_stamp_float())
    return token
