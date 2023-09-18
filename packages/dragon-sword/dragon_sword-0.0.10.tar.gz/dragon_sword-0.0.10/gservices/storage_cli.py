from io import BytesIO

from gservices.errno import FILE_SHA2
from gservices.registry_cli import ServiceClient, Service
from gservices import storage_pb2 as pb
from gservices.storage_pb2_grpc import StorageServiceStub
from gservices.storage_utils import save_file
from gservices.utils import check_code
from utils.file import (
    read_file_iter, is_compress_file, get_path_last_part,
    sha2_io, sha2_file, extract_compressed,
    rm_file,
)
from utils.errno import Error, OK

_Worker = "worker"


def _iter_upload_req(token, task_id, filepath: str, need_unpack: bool, server: str = _Worker):
    yield pb.UploadReq(token=token)
    yield pb.UploadReq(task_id=task_id)
    b = BytesIO()
    for chunk in read_file_iter(filepath):
        b.write(chunk)
        yield pb.UploadReq(chunk=chunk)
    yield pb.UploadReq(meta=pb.FileUMeta(
        filename=get_path_last_part(filepath),
        need_unpack=need_unpack,
        sha2=sha2_io(b),
        server=server,
    ))


class _StorageCli(ServiceClient):
    def __init__(self):
        super().__init__(StorageServiceStub, "cook.storage")

    def upload(self, token: str, task_id: str, filepath: str, need_unpack=False,
               tags: dict[str, set] = None) -> tuple[pb.UploadRes, Error]:
        res, err = self.do_request(task_id, _iter_upload_req(token, task_id, filepath, need_unpack), "Upload", tags=tags)
        return res, err

    def download(self, token: str, task_id: str, filename: str, filepath: str,
                 tags: dict[str, set] = None) -> tuple[pb.DownloadRes, Error]:
        req = pb.DownloadReq(
            token=token,
            task_id=task_id,
            meta=pb.FileDMeta(filename=filename, filepath=filepath, server=_Worker)
        )
        res, err = self.do_request(task_id, req, "Download", tags=tags)
        return res, err


StorageCli = _StorageCli()


def upload(token: str, task_id: str, filepath: str, tags: dict[str, set]) -> Error:
    res, err = StorageCli.upload(token, task_id, filepath, tags=tags)
    if not err.ok:
        return err
    err = check_code(res)
    if not err.ok:
        return err
    return OK


def download(token: str, task_id: str, filename: str, dest_filepath,
             tags: dict[str, set], filepath: str = ""):
    res, err = StorageCli.download(token, task_id, filename, filepath, tags)
    if not err.ok:
        return err
    status, sha2 = save_file(res, dest_filepath, ret_code=True)
    err = check_code(status)
    if not err.ok:
        return err
    if sha2_file(dest_filepath) != sha2:
        return FILE_SHA2
    if is_compress_file(dest_filepath):
        err = extract_compressed(dest_filepath)
        if not err.ok:
            return err
        rm_file(dest_filepath)
    return OK
