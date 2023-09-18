import contextlib
import glob
import hashlib
import json
import os
import shutil
import stat
import threading
import traceback
import zipfile
from subprocess import call
# from fcntl import LOCK_EX, LOCK_UN, LOCK_SH, flock
# import portalocker
from typing import BinaryIO

import yaml

from utils.data import is_num
from utils.errno import (
    Error, OK,
    MISS_ZIP, BROKEN_ZIP, BROKEN_JSON, MISS_JSON,
    COPY_FILE, COPY_FILE_EXIST, NO_FILE,
)
from utils.log import logger
from utils.system import is_win


class Lock:
    def __init__(self, directory):
        self._file_name = os.path.join(directory, "_cook_server_lock")
        self._fd = open(self._file_name, 'w')

    def _record(self):
        self._fd.write(f"{os.getpid()}\n{threading.current_thread().ident}")

    @contextlib.contextmanager
    def read_lock(self):
        self.lock()
        yield
        # flock(self._fd, LOCK_SH)
        # with portalocker.Lock(self._file_name) as f:
        #     yield
        self.unlock()

    @contextlib.contextmanager
    def write_lock(self):
        self.lock()
        self._record()
        yield
        self.unlock()
        # TODO: LOCK_NB非阻塞
        # flock(self._fd, LOCK_EX)
        # self._record()

    def lock(self):
        pass

    def unlock(self):
        pass
        # flock(self._fd, LOCK_UN)
        # self._fd.write("")
        # self._fd.close()

    def __del__(self):
        try:
            self._fd.close()
        except Exception as e:
            logger.error(f"Lock del err={e}")


def norm_path(path: str) -> str:
    return os.path.normpath(path)


def norm_case_insensitive_path(path: str) -> str:
    path = path.lower()
    return norm_path(path)


def norm_spe(path: str) -> str:
    return path.replace(os.path.sep, "/")


def check_path_exist(path: str) -> bool:
    """
    校验文件是否存在，若filepath是路径且存在，也会返回True
    :param path:
    :return:
    """
    if not os.path.exists(norm_path(path)):
        # logger.error(f"1 check_file_exist no file {path}")
        return False
    return True


def abs_path(path: str) -> str:
    return os.path.abspath(path)


def check_file_exist(path: str) -> bool:
    """
    校验文件存在且是文件，而不仅仅是路径
    :param path:
    :return:
    """
    return check_path_exist(path) and is_file(path)


def is_file(path: str) -> bool:
    # isfile若文件不存在，也会返回false
    return os.path.isfile(path) or "." in path


_compress_suffix = {"gz", "tar", "zip", "rar", "tar.gz"}


def is_compress_file(filepath: str) -> bool:
    if "." not in filepath:
        return False
    suffix = filepath.split('.')[-1]
    return suffix in _compress_suffix


def check_zip_file(filepath: str) -> Error:
    """
    校验文件是否是完好的zip文件
    :param filepath:
    :return:
    """
    if not check_file_exist(filepath):
        return MISS_ZIP
    try:
        zip_f = zipfile.ZipFile(filepath)
    except Exception as e:
        logger.error(f"check_zip_file {filepath} get broken zip {e}")
        return BROKEN_ZIP
    else:
        if zip_f.testzip() is not None:
            logger.error(f"check_zip_file {filepath} get broken file")
            return BROKEN_ZIP
    return OK


def read_file_iter(filename: str):
    if not check_file_exist(filename):
        yield
        return
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(buff_size())
            if not chunk:
                break
            yield chunk


def load_f(filename: str) -> tuple[str, Error]:
    if not check_file_exist(filename):
        return "", NO_FILE
    with open(filename, "r", encoding="utf-8") as f:
        return f.read(), OK


_text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})


def is_binary_f(filepath: str) -> bool:
    if not check_file_exist(filepath):
        return False
    with open(filepath, "rb") as f:
        b = f.read(1024)
    return bool(b.translate(None, _text_chars))


def is_binary_f2(filepath: str) -> bool:
    if not check_file_exist(filepath):
        return False
    try:
        with open(filepath, "r") as f:
            f.read(1024)
            return True
    except UnicodeDecodeError:
        return False


def load_f_line(filename: str) -> tuple[list[str], Error]:
    if not check_file_exist(filename):
        return [], NO_FILE
    with open(filename, "r", encoding="utf-8") as f:
        return [item.strip() for item in f.readlines()], OK


def dump_f(filename: str, s: str) -> Error:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(s)
    return OK


def dump_b_f(filename: str, b: bytes) -> Error:
    with open(filename, "wb") as f:
        f.write(b)
    return OK


def dump_f_lines(filename: str, ss: list[str]) -> Error:
    ss = [f"{s.strip()}\n" for s in ss]
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(ss)
    return OK


def f_other_format(filename: str, _format: str) -> str:
    root, ext = os.path.splitext(filename)
    if not _format:
        return root
    return f"{root}.{_format}"


def append_f_line(filename: str, line: str) -> Error:
    line = line.strip()
    with open(filename, "a") as f:
        f.write(f"{line}\n")
    return OK


def load_json_f(filename: str) -> tuple[dict, Error]:
    """
    加载json文件
    :param filename:
    :return:
    """
    res = {}
    if not check_file_exist(filename):
        return res, MISS_JSON
    with open(filename, "r", encoding="utf-8") as f:
        err = OK
        try:
            res = json.load(f)
        except ValueError:
            err = BROKEN_JSON
            logger.error(f"load_json_f {filename} broken json")
    return res, err


def dump_json_f(filename: str, _dict: dict) -> Error:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(_dict, f, ensure_ascii=False)
    return OK


def compare_json_f(path1: str, path2: str, exclude_field: set = None) -> bool:
    if not exclude_field:
        exclude_field = {}
    json1, err = load_json_f(path1)
    if not err.ok:
        logger.error(f"!!!!!!!!!no {path1}")
        return False
    json2, err = load_json_f(path2)
    if not err.ok:
        logger.error(f"!!!!!!!!!no {path2}")
        return False
    for k, v in json1.items():
        if k in exclude_field:
            continue
        if v != json2.get(k):
            return False
    return True


def sha2_io(f: BinaryIO) -> str:
    """
    计算内存中内容的sha256
    :param f:
    :return:
    """
    f.seek(0)
    sha2 = hashlib.sha256()
    buf_size = 65536
    while True:
        data = f.read(buf_size)
        if not data:
            break
        sha2.update(data)
    return sha2.hexdigest()


def sha2_file(filepath: str) -> str:
    """
    计算文件的sha256
    :param filepath:
    :return:
    """
    if not check_file_exist(filepath):
        return ""
    with open(filepath, "rb") as f:
        return sha2_io(f)


def tran_json_to_yml_f(json_path: str, yml_path: str):
    """
    json文件转换为yaml文件
    :param json_path:
    :param yml_path:
    :return:
    """
    yml_path = norm_path(yml_path)
    logger.info(f"tran_json_to_yml_f {json_path} to {yml_path}")
    if not check_file_exist(json_path):
        logger.error(f"trans_json_to_yml_f no {json_path}, do nothing")
        return
    if os.path.exists(yml_path):
        logger.error(f"trans_json_to_yml_f {yml_path} exist, do nothing")
        return

    with open(json_path, encoding="utf-8") as f:
        conf = json.load(f)

    with open(yml_path, 'w', encoding="utf-8") as f:
        yaml.dump(conf, f, allow_unicode=True, default_flow_style=False)


def is_remote_path(path):
    """ 判断一个路径是不是远程路径，以"\\"开头，注意："\\\\127.0.0.1\\xxx" 也会认为是远程路径。
    """
    path = norm_path(path)
    return path.startswith(r"\\")


def my_listdir(path, list_name):  # 传入存储的list
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            my_listdir(file_path, list_name)
        else:
            list_name.append(file_path)


def copy_param_files(source_path, target_path):
    # target_path = target_path.replace("\\", "/")

    # logger.info("copy_param_files! source_path = " + source_path)
    # logger.info("copy_param_files! target_path = " + target_path)

    # shutil.copytree(source_path, target_path)

    # try:
    #     shutil.copytree(source_path, target_path)
    # except err:
    #     logger.info("err = " + str(err))

    # for root, dirs, files in os.walk(source_path):
    #     logger.info("dirs = " + dirs)
    #     for file in files:
    #         src_file = os.path.join(root, file)
    #         shutil.copy(src_file, target_path)
    #         logger.info("src_file = " + src_file)
    #         logger.info("target_path = " + target_path)

    names = os.listdir(source_path)
    for name in names:
        srcname = os.path.join(source_path, name)
        dstname = os.path.join(target_path, name)
        if os.path.isdir(srcname):
            if os.path.exists(dstname):
                continue
            else:
                shutil.copytree(srcname, dstname)
        else:
            # file
            shutil.copy(srcname, dstname)


def _split_all_path(file_path: str) -> list[str]:
    _path = []
    if is_win():
        driver, file_path = os.path.splitdrive(file_path)
        if driver:
            driver = f"{driver}\\"
    else:
        file_path = file_path.replace("\\\\", "/")
        file_path = file_path.replace("\\", "/")
        if file_path.startswith("/"):
            driver = "/"
        else:
            driver = ""

    head = file_path
    while head != "" and head != "\\" and head != "/":
        head, tail = os.path.split(head)
        _path.append(tail)
    if driver:
        # Linux目录，/c/test，/c不会被识别为driver
        _path.append(driver)
    _path.reverse()
    return _path


def dirs_in_dir(path: str) -> set[str]:
    return {p for p in os.listdir(path) if os.path.isdir(get_file_path(path, p))}


def full_dirs_in_dir(path: str) -> set[str]:
    result = set()
    for p in os.listdir(path):
        _p = get_file_path(path, p)
        if os.path.isdir(_p):
            result.add(_p)
    return result


def files_in_dir(path: str) -> set[str]:
    result = set()
    for p in os.listdir(path):
        _p = get_file_path(path, p)
        if os.path.isfile(_p):
            result.add(_p)
    return result


def filename_in_dir(path: str) -> set[str]:
    result = set()
    for p in os.listdir(path):
        _p = get_file_path(path, p)
        if os.path.isfile(_p):
            result.add(p)
    return result


def get_file_path(*paths) -> str:
    """
    获取文件路径，转换成系统统一格式
    :param paths:
    :return:
    """
    _path = []
    for p in paths:
        if is_num(p):
            _path.append(str(p))
            continue
        _path.extend(_split_all_path(p))
    p = os.path.join(*_path)
    return p


def get_path_parent(path: str) -> str:
    """
    获取路径的父路径，如d:/a/b/c/d，返回d:/a/b/c
    :param path:
    :return:
    """
    return os.path.join(*_split_all_path(path)[:-1])


def get_path_last_part(path) -> str:
    return _split_all_path(path)[-1]


def get_path_back_second_part(path) -> str:
    return _split_all_path(path)[-2]


def copy_file(source: str, dest: str) -> tuple[str, Error]:
    source = norm_path(source)
    dest = norm_path(dest)
    if not is_file(dest):
        dest = get_file_path(dest, get_path_last_part(source))
    if check_file_exist(dest):
        return dest, COPY_FILE_EXIST
    try:
        shutil.copyfile(source, dest)
    except IOError as e:
        logger.error(f"!!!!copy_file err={e}")
        return dest, COPY_FILE
    return dest, OK


def rename_f(source: str, dest: str) -> Error:
    if not check_path_exist(source):
        return OK
    os.rename(source, dest)
    return OK


def move_file(source: str, dest: str) -> Error:
    if not is_file(dest):
        dest = get_file_path(dest, get_path_last_part(source))
        logger.debug(f"move_file {dest} actually")
    shutil.move(source, dest)
    return OK


def move_file_in_dir(source: str, dest: str) -> Error:
    for filepath in files_in_dir(source):
        move_file(filepath, dest)
    return OK


def make_dirs(path: str) -> Error:
    if check_path_exist(path):
        return OK
    path = norm_path(path)
    os.makedirs(path)
    os.chmod(path, stat.S_IRWXO)
    return OK


def _remove_readonly(func, path, _):
    """
    Clear the readonly bit and reattempt the removal
    :param func:
    :param path:
    :param _:
    :return:
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rm_dirs(path: str) -> Error:
    # logger.debug(f"===============rm_dirs {path}")
    path = get_file_path(path)
    try:
        shutil.rmtree(path, onerror=_remove_readonly)
    except Exception:
        logger.error(f"rm_dirs {path} err={traceback.format_exc()}")
    return OK


def rm_file(filename: str) -> Error:
    filename = get_file_path(filename)
    if not check_file_exist(filename):
        return OK
    os.remove(filename)
    return OK


def extract_compressed(path: str, target_path: str = None) -> Error:
    """
    解压压缩文件
    :param target_path:
    :param path:
    :return:
    """
    if not target_path:
        target_path = os.path.dirname(path)
    shutil.unpack_archive(path, target_path)
    return OK


def compress(path: str, target_path: str = None) -> tuple[str, Error]:
    path = get_file_path(path, "")
    if target_path is None:
        target_path = f"{path}"
    shutil.make_archive(target_path, "zip", path)
    return f"{target_path}.zip", OK


def copy_dir(src, dest, override=False):
    src = norm_path(src)
    dest = norm_path(dest)

    count = 0
    if not check_path_exist(dest):
        os.mkdir(dest)
    items = glob.glob(get_file_path(src, '*'))
    for item in items:
        if os.path.isdir(item):
            path = get_file_path(dest, get_path_last_part(item))
            count += copy_dir(src=item, dest=path, override=override)
        else:
            file = os.path.join(dest, get_path_last_part(item))
            if not check_file_exist(file) or override:
                shutil.copyfile(item, file)
                count += 1
    return count


def cmp_file(f1: str, f2: str) -> bool:
    st1 = os.stat(f1)
    st2 = os.stat(f2)
    # 比较文件大小
    if st1.st_size != st2.st_size:
        return False
    size = 8 * 1024
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(size)  # 读取指定大小的数据进行比较
            b2 = fp2.read(size)
            if b1 != b2:
                return False
            if not b1:
                return True


def buff_size() -> int:
    return 65536


def get_f_time(filepath: str) -> tuple[float, float]:
    """
    :param filepath:
    :return: 文件创建时间，文件修改时间
    """
    s = os.stat(filepath)
    return s.st_ctime, s.st_mtime


def get_f_last_line(filepath: str) -> str:
    with open(filepath, "rb") as f:
        try:  # catch OSError in case of a one line file
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        return f.readline().decode(encoding="utf-8")


def link(source: str, target: str) -> Error:
    f1 = not check_path_exist(source)
    f2 = check_path_exist(target)
    if f1 or f2:
        logger.debug(f"link do nothing {f1} {f2}")
        return OK

    if not is_win():
        os.symlink(source, target)
        return OK

    call(["mklink", "/J", target, source], shell=True)
    return OK
