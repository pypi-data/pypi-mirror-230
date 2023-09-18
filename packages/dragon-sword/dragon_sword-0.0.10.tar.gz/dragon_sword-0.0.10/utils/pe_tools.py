# encoding=utf8

import os
from utils.log import logger


# 字符串转换成左斜线，并且全小写
# eg: "C:\aaa\BBB.txt" -> "c:/aaa/bbb"
# pe_tools.path_lower_normalize
def path_lower_normalize(path):
    if not path:
        logger.error("[Error][pe_tools.path_lower_normalize] path is empty!")
        return None
    path = path.lower()
    path = os.path.normpath(path)
    path = path.replace(os.path.sep, "/")
    return path

def path_normalize(path):
    if not path:
        logger.error("[Error][pe_tools.path_lower_normalize] path is empty!")
        return None
    #path = path.lower()
    path = os.path.normpath(path)
    path = path.replace(os.path.sep, "/")
    return path


def to_local_job_path(path, local_houdini_projs_dir):
    """ 解决跨平台问题，根据当前平台替换path前部分"d:/HoudiniProject"或者"/root/..."
    """
    if not path:
        logger.error("[Error][pe_tools.job_path_normalize] path is empty!")
        return None

    idx = path.lower().find("houdiniprojects")
    if idx != -1:
        path = os.path.join(local_houdini_projs_dir, path[idx + len("houdiniprojects") + 1:])

    return path