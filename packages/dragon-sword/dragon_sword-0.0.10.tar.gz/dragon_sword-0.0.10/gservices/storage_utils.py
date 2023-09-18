from gservices import storage_pb2 as pb
from utils.log import logger


def _save_file(res, fd, ret_code) -> tuple[pb.Status, str]:
    sha2 = ""
    status = pb.Status()
    for c in res:
        if (ret_code and c.status.message) \
                or (not ret_code and c.status.check_desc):
            logger.debug(f"status={c.status}")
            status = c.status
        elif c.meta.sha2:
            logger.debug(f"meta={c.meta}")
            sha2 = c.meta.sha2
        elif c.chunk:
            fd.write(c.chunk)
    return status, sha2


def save_file(res, filepath: str, ret_code=False) -> tuple[pb.Status, str]:
    with open(filepath, "wb") as f:
        return _save_file(res, f, ret_code)
