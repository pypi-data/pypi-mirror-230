from utils.errno import Error

FILE_SHA2 = Error(1500, "ERR_FILE_SHA2", "文件sha256校验不一致")
FILE_NO_NAME = Error(1501, "ERROR_FILE_NO_NAME", "文件没有名")
NO_INSTANCE = Error(3003, "ERR_NO_INSTANCE", "无可用实例")
