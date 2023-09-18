# -*- encoding:utf-8 -*-
# 实时语音转写
# https://www.xfyun.cn/doc/asr/rtasr/API.html
import base64
import hashlib
import hmac
import json
import threading
import time
import websocket
from websocket import create_connection

from utils.url import dict_to_param
from third_party.wrm.log import logger


class Client:
    def __init__(self, queue, app_id, api_key):
        self._q = queue
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        signa = self.__sign(api_key, app_id, ts)
        self.end_tag = "{\"end\": true}"

        param = {
            "appid": app_id,
            "ts": ts,
            "signa": signa,
            # 开角色分离
            "roleType": 2,
        }
        u = f"{base_url}?{dict_to_param(param)}"
        self.ws = create_connection(u)
        self.trecv = threading.Thread(target=self.receive)
        self.trecv.start()

    @staticmethod
    def __sign(api_key, app_id, ts):
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        base_str = md5.hexdigest()
        base_str = bytes(base_str, encoding='utf-8')
        api_key = api_key.encode('utf-8')
        sign = hmac.new(api_key, base_str, hashlib.sha1).digest()
        sign = base64.b64encode(sign)
        sign = str(sign, 'utf-8')
        return sign

    def send(self, file_path):
        file_object = open(file_path, 'rb')
        try:
            index = 1
            while True:
                chunk = file_object.read(1280)
                if not chunk:
                    break
                self.ws.send(chunk)

                index += 1
                time.sleep(0.04)
        finally:
            file_object.close()

        self.ws.send(bytes(self.end_tag.encode('utf-8')))
        logger.info("send end tag success")

    def receive(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    logger.info("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    logger.info("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    self._q.put(result_dict["data"])

                if result_dict["action"] == "error":
                    logger.info("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            logger.error("receive result end")

    def close(self):
        self.ws.close()
        logger.info("connection closed")
