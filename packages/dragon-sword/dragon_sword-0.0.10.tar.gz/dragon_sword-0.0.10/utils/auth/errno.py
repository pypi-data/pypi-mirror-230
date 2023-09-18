from utils.errno import Error

TOKEN_EMPTY = Error(1300, "ERR_TOKEN", "token不存在")
TOKEN_EXPIRE = Error(1301, "ERR_TOKEN", "token失效")
USER_EMPTY = Error(1302, "ERR_USER_EMPTY", "用户名或密码错误，请确认用户名或密码")
USER_PWD = Error(1303, "ERR_USER_PWD", "用户名或密码错误，请确认用户名或密码")
PROJ_EMPTY = Error(1304, "ERR_PROJ_EMPTY", "项目不存在")
TOKEN_B64_DECODE = Error(1305, "ERR_TOKEN_B64_DECODE", "token无法base64解码")
TOKEN_NOT_UTF8 = Error(1306, "ERR_TOKEN_NOT_UTF8", "token存在非法utf8字符")
TOKEN_LENGTH = Error(1307, "ERR_TOKEN_LENGTH", "token长度非法")
TOKEN_EXPIRED = Error(1308, "ERR_TOKEN_EXPIRED", "token已失效")
TOKEN_NO_USER = Error(1309, "ERR_TOKEN_NO_USER", "token未找到对应用户")
