from urllib.parse import urlparse
from utils.file import get_path_last_part


def url_f_name(u: str) -> str:
    return get_path_last_part(urlparse(u).path)
