from utils.errno import Error

WPS_BAD_REQ = Error(2000, "ERR_WPS_BAD_REQ", "wps接口请求失败")
WPS_EMPTY_RES = Error(2001, "ERR_WPS_EMPTY_RES", "wps接口返回空结果")
WPS_NOT_JSON = Error(2002, "ERR_WPS_NOT_JSON", "wps接口返回非json")
