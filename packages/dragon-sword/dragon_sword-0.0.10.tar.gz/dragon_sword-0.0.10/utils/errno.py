class Error(object):
    def __init__(self, code_int: int, code: str, desc: str = ""):
        self.code_int = code_int
        self.code = code
        self.desc = desc

    @property
    def ok(self):
        return self.code_int == 0

    def __str__(self):
        return f"code={self.code_int} message={self.code}:{self.desc}"


def check_errors(errors: list[Error]) -> list[int]:
    result = []
    for i in range(len(errors)):
        err = errors[i]
        if isinstance(err, Error) and not err.ok \
                or isinstance(err, Exception):
            result.append(i)
    return result


OK = Error(0, "", "")
INTERVAL_SERVER = Error(500, "Internal Server Error", "服务内部错误，请联系管理员")
TIMEOUT = Error(599, "TIMEOUT", "超时")

MISS_CONFIG = Error(1000, "ERR_MISS_CONFIG", "配置文件丢失")
BROKEN_CONFIG = Error(1001, "ERR_BROKEN_CONFIG", "配置文件损坏")
MISS_ZIP = Error(1002, "ERR_MISS_ZIP", "zip丢失")
BROKEN_ZIP = Error(1003, "ERR_BROKEN_ZIP", "zip已损坏")
BROKEN_JSON = Error(1004, "ERR_BROKEN_JSON", "json文件已损坏")
MISS_JSON = Error(1005, "ERR_MISS_JSON", "json文件丢失")
COPY_FILE = Error(1006, "ERR_COPY_FILE", "文件拷贝失败")
NO_FILE = Error(1007, "ERR_NO_FILE", "文件不存在")
THIRD_SERVER = Error(1008, "ERR_THIRD_SERVER", "三方服务出错")
CONFIG_NO_FIELD = Error(1009, "ERR_CONFIG_NO_FIELD", "配置文件缺少配置项")
COPY_FILE_EXIST = Error(1010, "ERR_COPY_FILE_EXIST", "拷贝目标文件已存在")
REQ_PARAM = Error(1011, "ERR_REQ_PARAM", "请求参数错误")
TRANS_MP4 = Error(1012, "ERR_TRANS_MP4", "转换mp4错误")
DOWNLOAD = Error(1013, "ERR_DOWNLOAD", "ffmpeg下载失败")
NO_M3U8 = Error(1014, "ERR_NO_M3U8", "缺少m3u8文件")
NO_TS = Error(1015, "ERR_NO_TS", "缺少ts文件")
TS_ERR = Error(1016, "ERR_TS", "ts文件内容错误")
WEB_ELEMENT = Error(1017, "ERR_WEB_ELEMENT", "页面内容元素错误")

# 已占用号段
# model.errno 1400-1499 2100-2199
# uservices.errno 1500-1599 3000-3099
# thirdparty.wps.errno 2000-2099
# thirdparty.tencent_cloud.errno 2100-2199
# auth.errno 1300-1399
FLOW_LIMIT_NO_TOKEN = Error(3001, "ERR_FLOW_LIMIT_NO_TOKEN", "限流无token")
FLOW_LIMIT_NO_ACQUIRED = Error(3002, "ERR_FLOW_LIMIT_NO_ACQUIRED", "限流续期无token")
