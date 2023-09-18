import re
import zlib
import hashlib
import uuid


def format_file_name(name: str) -> str:
    """
    规范化文件名中，一些会导致显示异常的字符
    :param name:
    :return:
    """
    name = name.replace("\n", " ").replace("\r\n", " ")
    # -不能换成_
    name = name.replace("……", "_").replace('"', "_").replace("'", "_") \
        .replace("！", " ").replace("!", " ") \
        .replace(",", " ").replace(".", " ") \
        .replace("，", " ").replace("。", " ") \
        .replace("[", " ").replace("]", " ") \
        .replace("【", " ").replace("】", " ")

    name = name.strip()
    name = ' '.join(name.split())
    name = name.replace(" ", "_")
    return name


def md5(text):
    encode_pwd = text.encode()
    md5_pwd = hashlib.md5(encode_pwd)
    return md5_pwd.hexdigest()


def str_to_int(s: str):
    m = md5(s)
    return int(m, 16)


def is_num(s) -> bool:
    return isinstance(s, int) or isinstance(s, float) or s.replace('.', '', 1).isdigit()


def uniq_id() -> str:
    return uuid.uuid1().hex


def decode_gzip(b: bytes) -> bytes:
    try:
        return zlib.decompress(b, 16 + zlib.MAX_WBITS)
    except zlib.error:
        return b


def decode_bytes(b: bytes) -> tuple[str, bool]:
    try:
        return b.decode("utf-8"), True
    except UnicodeDecodeError:
        return "", False


def get_ints_in_str(s: str) -> list[int]:
    ss = re.findall(r'\d+', s)
    result = []
    for s in ss:
        if is_num(s):
            result.append(int(s))
    return result


class LowStr(str):
    def __new__(cls, s: str):
        return str.__new__(cls, s.lower())
