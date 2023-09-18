import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models
from utils.errno import OK, Error
from third_party.errno import TencentCloudReqFail


from utils.log import logger


class _DnsPodClient(object):
    def __init__(self):
        self._sid = ""
        self._skey = ""
        self._cli = None

    def init(self, sid: str, skey: str):
        self._sid = sid
        self._skey = skey
        cred = credential.Credential(self._sid, self._skey)
        http_profile = HttpProfile(endpoint="dnspod.tencentcloudapi.com")
        cli_profile = ClientProfile(httpProfile=http_profile)
        self._cli = dnspod_client.DnspodClient(cred, "", cli_profile)

    @staticmethod
    def _get_line():
        return "默认"

    @staticmethod
    def _get_type(is_ipv4: bool):
        if is_ipv4:
            return "A"
        else:
            return "AAAA"

    def create(self, domain: str, subdomain: str, value: str, is_ipv4=False):
        req = models.CreateRecordRequest()
        params = {
            "Domain": domain,
            "SubDomain": subdomain,
            "RecordType": self._get_type(is_ipv4),
            "RecordLine": self._get_line(),
            "Value": value
        }
        req.from_json_string(json.dumps(params))

        result = ""
        err = OK
        try:
            resp = self._cli.CreateRecord(req)
            result = resp.to_json_string()
        except TencentCloudSDKException as e:
            logger.error("create fail %s", e)
            err = TencentCloudReqFail
        return result, err

    def update(self, record_id: int, domain: str, subdomain: str, value: str, is_ipv4=False) -> tuple[str, Error]:
        req = models.ModifyRecordRequest()
        # 必须传subdomain，否则更新会变成@
        params = {
            "Domain": domain,
            "SubDomain": subdomain,
            "RecordType": self._get_type(is_ipv4),
            "RecordLine": self._get_line(),
            "Value": value,
            "RecordId": record_id
        }
        req.from_json_string(json.dumps(params))

        result = ""
        err = OK
        try:
            resp = self._cli.ModifyRecord(req)
            result = resp.to_json_string()
        except TencentCloudSDKException as e:
            logger.error("update fail %s", e)
            err = TencentCloudReqFail
        return result, err

    def get(self, domain, subdomain, is_ipv4=False):
        req = models.DescribeRecordListRequest()
        # 注意这里的D是小写
        params = {"Domain": domain, "Subdomain": subdomain, "RecordType": self._get_type(is_ipv4)}
        req.from_json_string(json.dumps(params))

        result = ""
        err = OK
        try:
            resp = self._cli.DescribeRecordList(req)
            result = resp.to_json_string()
        except TencentCloudSDKException as e:
            logger.error("get fail %s", e)
            err = TencentCloudReqFail
        return result, err


DnsPodClient = _DnsPodClient()
