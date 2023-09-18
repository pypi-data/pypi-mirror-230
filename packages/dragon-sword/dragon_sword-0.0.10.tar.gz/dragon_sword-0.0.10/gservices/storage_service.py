import traceback
import storage_pb2 as pb
import storage_pb2_grpc as pb_grpc
from utils.errno import NO_FILE, OK, INTERVAL_SERVER
from gservices.errno import FILE_SHA2
from utils.file import (
    get_file_path, check_file_exist, sha2_file,
    check_path_exist, make_dirs, extract_compressed,
    read_file_iter
)
from gservices.decorator import catch_decorator
from gservices.utils import trans_ret_code
from utils.log import logger


class StorageService(pb_grpc.StorageServiceServicer):
    """
    存储服务
    """
    def __init__(self, doc, download_pre, upload_mid):
        self._doc = doc
        self.download_pre = download_pre
        self.upload_mid = upload_mid
        super().__init__()

    def Download(self, req: pb.DownloadReq, context) -> pb.DownloadRes:
        """
        下载烘焙文件压缩包
        :param req:
        :param context:
        :return:
        """
        try:
            task_dir, filename, err = self.download_pre(req.token, req.task_id, req.meta)
            if not err.ok:
                yield pb.DownloadRes(status=trans_ret_code(pb.Status, err))
                yield pb.DownloadRes(doc=self._doc)
            else:
                filepath = get_file_path(task_dir, req.meta.filepath, filename)
                if not check_file_exist(filepath):
                    yield pb.DownloadRes(status=trans_ret_code(pb.Status, NO_FILE))
                    yield pb.DownloadRes(doc=self._doc)
                else:
                    sha2 = sha2_file(filepath)
                    yield pb.DownloadRes(status=trans_ret_code(pb.Status, OK))
                    yield pb.DownloadRes(meta=pb.FileDMeta(sha2=sha2))
                    yield pb.DownloadRes(doc=self._doc)
                    for chunk in read_file_iter(filepath):
                        yield pb.DownloadRes(chunk=chunk)
        except Exception as e:
            logger.error(f"StorageService Download raise err={e} \n {traceback.format_exc()}")
            yield pb.DownloadRes(status=trans_ret_code(pb.Status, INTERVAL_SERVER))

    @catch_decorator(pb.UploadRes)
    def Upload(self, req_iter: pb.UploadReq, context) -> pb.UploadRes:
        """
        上传文件
        :param req_iter:
        :param context:
        :return:
        """
        data = bytearray()
        token: str = None
        task_id: str = None
        meta: pb.FileUMeta = None

        i = 0
        for req in req_iter:
            i += 1
            if req.token:
                logger.debug(f"{i} token={req.token};")
                token = req.token
            elif req.task_id:
                logger.debug(f"{i} uuid={req.task_id};")
                task_id = req.task_id
            elif req.meta.filename:
                logger.debug(f"{i} meta={req.meta}; {type(req.meta)}")
                meta = req.meta
            elif req.chunk:
                data.extend(req.chunk)
            if token is not None and task_id is not None and meta is not None:
                break

        task_dir, err = self.upload_mid(token, task_id, meta)
        if not err.ok:
            ret = trans_ret_code(pb.UploadRes, err)
            ret.doc = self._doc
            return ret

        filepath = get_file_path(task_dir, meta.filepath)
        if not check_path_exist(filepath):
            make_dirs(filepath)
        filepath = get_file_path(filepath, meta.filename)

        with open(filepath, "wb") as f:
            f.write(data)
            for req in req_iter:
                if not req.chunk:
                    continue
                f.write(req.chunk)

        sha2 = sha2_file(filepath)
        if meta.sha2:
            if sha2 != meta.sha2:
                logger.error(f"check sha2 {meta.sha2} != {sha2}")
                ret = trans_ret_code(pb.UploadRes, FILE_SHA2)
                ret.doc = self._doc
                return ret

        if meta.need_unpack:
            logger.debug(f"unpack {filepath}")
            extract_compressed(filepath)

        logger.debug("Upload end")
        ret = trans_ret_code(pb.UploadRes, OK)
        ret.sha2 = sha2
        ret.doc = self._doc
        return ret
