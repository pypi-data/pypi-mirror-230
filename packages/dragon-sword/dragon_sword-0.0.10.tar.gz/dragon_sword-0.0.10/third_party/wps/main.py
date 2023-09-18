from typing import Type

from third_party.wps._client import _Client
from third_party.wps.errno import WPS_EMPTY_RES
from utils.config import get_conf, get_default
from utils.data import Cache
from utils.errno import Error, OK
from utils.time import get_now_stamp, get_stamp_after
from utils.log import logger

_ConfFields = ("app_id", "app_key", "host")


class _Wps(Cache):
    def __init__(self):
        super().__init__()
        self._enable: bool
        self._cli: _Client
        self._chats: list

        # 下面俩不需要self.get，请求中动态缓存
        self._company_token = None
        self._company_valid_stamp = 0

    @property
    def cli(self):
        return self.get("_cli")

    @property
    def enable(self):
        return self.get("_enable")

    @property
    def chats(self):
        return self.get("_chats")

    def _load(self):
        conf = get_conf("notify")
        conf = get_default(conf, "wps", {})

        self._enable = get_default(conf, "enable", False)
        if not self._enable:
            logger.debug(f"_Wps init dummy WPS")
            return

        for f in _ConfFields:
            if f not in conf:
                logger.error(f"init_wps no {f}")
                return

        self._cli = _Client(conf["app_id"], conf["app_key"], conf["host"])
        self._chats = get_default(conf, "chats", [])

    def get_company_uid(self, company_token: str, access_token: str) -> (Type[Error], str):
        """
        doc: https://docs.oa.wanmei.net/woa-open/pages-pri/server/contacts/users/get-company-uid/
        :param company_token:
        :param access_token:
        :return:
        """
        if not self.enable:
            logger.debug(f"get_company_uid do nothing")
            return OK, ""

        u = "/plus/v1/company/user/company_uid"
        q = {"company_token": company_token, "access_token": access_token}
        err, msg, rsp = self.cli.req(u, query=q)
        r = ""
        if err.ok:
            r = rsp.get("company_uid", "")
        else:
            logger.error(f"get_company_uid err={err} msg={msg}")
        if r == "":
            logger.error(f"get_company_uid get empty")
            err = WPS_EMPTY_RES
        return err, r

    def _company_token_ok(self):
        return self._company_token and get_now_stamp() < self._company_valid_stamp

    def get_group_chat_list(self, company_token: str) -> (Type[Error], list[tuple]):
        """
        doc: https://docs.oa.wanmei.net/woa-open/pages-pri/server/msg-and-group/get-groupchat-list/
        :return:
        """
        if not self.enable:
            logger.debug(f"get_group_chat_list do nothing")
            return OK, []

        u = "/kopen/woa/api/v2/developer/app/chats"
        q = {"company_token": company_token}
        err, msg, rsp = self.cli.req(u, query=q)
        r = []
        if err.ok:
            for c in rsp.get("chats", []):
                r.append((c["chat_id"], c["name"]))
        else:
            logger.error(f"get_group_chat_list err={err} msg={msg}")
        if len(r) == 0:
            logger.error(f"get_group_chat_list get empty")
            err = WPS_EMPTY_RES
        return err, r

    def get_company_token(self) -> (Type[Error], str):
        """
        code: https://docs.oa.wanmei.net/woa-open/pages-pri/server/API-certificate/company-token/org-app/
        :return:
        """
        if not self.enable:
            logger.debug(f"get_company_token do nothing")
            return OK, ""

        if self._company_token_ok():
            return OK, self._company_token

        with self._lock:
            if self._company_token_ok():
                return OK, self._company_token
            u = "/auth/v1/company/inner/token"
            q = {"app_id": self.cli.app_id}
            err, msg, rsp = self.cli.req(u, query=q)
            r = ""
            expire_sec = 0
            if err.ok:
                token = rsp.get("token", {})
                expire_sec = token.get("expires_in", 0)
                r = token.get("company_token", "")
            else:
                logger.error(f"get_company_token err={err} msg={msg}")
            if r == "":
                err = WPS_EMPTY_RES
                logger.error(f"get_company_token get no token {rsp}")
            else:
                self._company_token = r
                # 减去10秒，防止临界
                self._company_valid_stamp = get_stamp_after(get_now_stamp(), second=max(expire_sec - 10, 0))
        return err, r

    def send_msg_to_chat(self, company_token: str, msg: str) -> (Type[Error], str):
        """
        doc: https://docs.oa.wanmei.net/woa-open/pages-pri/server/msg-and-group/sendmsgV2/
        :param company_token:
        :param msg:
        :return:
        """
        if not self.enable:
            logger.debug(f"send_msg_to_chat do nothing")
            return OK, ""

        chats = self.chats
        if not chats:
            logger.debug(f"wps send_msg_to_chat no chats from config")
            return OK, ""

        err = OK
        r = ""
        for c in chats:
            chat_ids = [c["id"]]
            u = "/kopen/woa/v2/dev/app/messages"
            q = {"company_token": company_token}
            b = {"app_key": self.cli.app_id, "to_chats": chat_ids, "msg_type": 1,
                 "content": {"type": 1, "body": msg}}
            err, msg, rsp = self.cli.req(u, method="POST", query=q, body=b)
            r = ""
            if err.ok:
                r = rsp.get("message_id", "")
            else:
                logger.error(f"send_msg_to_chat code={err} msg={msg}")
            if r == "":
                err = WPS_EMPTY_RES
                logger.error(f"send_msg_to_chat get no msg id {rsp}")
            logger.debug(f"notify_by_woa code={err} msg id={r}")
        return err, r


WPS = _Wps()
