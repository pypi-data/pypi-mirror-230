import requests
import urllib.parse
from utils.data import Cache
from utils.config import get_conf, get_default
from utils.log import logger


class _YouDu(Cache):
    def __init__(self):
        super().__init__()
        self._enable: bool
        self._host: str
        self._sender: str
        self._userid: str

    def _load(self):
        conf = get_conf("notify")
        conf = get_default(conf, "youdu", {})

        self._enable = get_default(conf, "enable", False)
        if not self._enable:
            logger.debug(f"_YouDu init dummy WPS")
            return

        self._host = conf["host"]
        self._sender = conf["sender"]
        self._userid = conf["userid"]

    def send_msg_to_chat(self, msg: str) -> str:
        if not self.get("_enable"):
            return ""
        message_json = {"sender": self.get("_sender"),
                        "content": urllib.parse.unquote(msg),
                        "userId": self.get("_userid"),
                        "groupName": "客服集中群"}
        headers = {"Content-Type": "application/json"}
        r = requests.post(self.get("_host"), json=message_json, headers=headers)
        return r.text


YouDu = _YouDu()
