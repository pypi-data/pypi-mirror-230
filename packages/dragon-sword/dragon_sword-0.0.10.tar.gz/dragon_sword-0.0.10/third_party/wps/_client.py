import hashlib
import json
import time
import urllib.parse
from typing import Type

import requests

from utils.errno import Error, OK
from third_party.wps.errno import WPS_BAD_REQ, WPS_NOT_JSON


class _Client(object):
    """
    WPS客户端
    """
    def __init__(self, app_id: str, app_key: str, host: str):
        self.app_id = app_id
        self._app_key = app_key
        self._host = host
        requests.packages.urllib3.disable_warnings()

    def _sig(self, content_md5: str, url: str, date: str):
        sha1 = hashlib.sha1(self._app_key.encode('utf-8'))
        sha1.update(content_md5.encode('utf-8'))
        sha1.update(url.encode('utf-8'))
        sha1.update("application/json".encode('utf-8'))
        sha1.update(date.encode('utf-8'))
        return f"WPS-3:{self.app_id}:{sha1.hexdigest()}"

    def req(self, uri, method: str = "GET", query: dict = None, body: dict = None,
            cookie: dict = None, headers: dict = None) -> (Type[Error], str, dict):
        if query is None:
            query = {}

        uri = f"{uri}?{urllib.parse.urlencode(query)}"

        if method == "PUT" or method == "POST" or method == "DELETE":
            body = json.dumps(body)

        if method == "PUT" or method == "POST" or method == "DELETE":
            content_md5 = hashlib.md5(body.encode('utf-8')).hexdigest()
        else:
            content_md5 = hashlib.md5("".encode('utf-8')).hexdigest()

        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        header = {"Content-type": "application/json",
                  'X-Auth': self._sig(content_md5, uri, date),
                  'Date': date,
                  'Content-Md5': content_md5}
        if headers:
            header = {}
            for key, value in headers.items():
                header[key] = value

        url = f"{self._host}/open{uri}"
        r = requests.request(method, url, data=body, headers=header, cookies=cookie, verify=False)
        err = OK
        msg = ""
        rsp = {}
        if r.status_code != 200:
            err = WPS_BAD_REQ
        else:
            try:
                rsp = json.loads(r.text)
                msg = rsp.get("msg", "OK")
            except ValueError:
                err = WPS_NOT_JSON
                msg = "not json"
        return err, msg, rsp
