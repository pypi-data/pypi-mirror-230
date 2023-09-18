import os
import urllib.request


def download_file(url: str, file_path: str):
    """_summary_

    Args:
        url (str): _description_
        file_path (str): _description_
    """
    return urllib.request.urlretrieve(url, file_path)


def download_u(u: str, out_path):
    if os.path.exists(out_path):
        return out_path
    download_file(u, out_path)
    return out_path
