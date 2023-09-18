import os
import traceback
from typing import Optional

from m3u8 import M3U8, load

from utils.async_req import DefaultHTTPClient, url_f_name
from utils.async_req import async_download
from utils.call import con_async, call_async
from utils.errno import Error, OK, NO_M3U8, NO_TS, TRANS_MP4, check_errors, TIMEOUT
from utils.file import (
    get_file_path, get_path_last_part, get_path_parent,
    check_file_exist,
    move_file, rm_dirs, rm_file,
    is_binary_f,
)
from utils.log import logger
from utils.server import Context
from .ffmpeg import _merge_local_m3u8

_M3u8HCli = DefaultHTTPClient()
M3u8FName = "index.m3u8"


def save_m3u8(u: str, filepath: str, timeout=3) -> Optional[M3U8]:
    try:
        m3u8 = load(u, http_client=_M3u8HCli, timeout=timeout)
    except Exception:
        logger.error(f"save_m3u8 {traceback.format_exc()}")
        return None
    else:
        m3u8.dump(filepath)
    return m3u8


def _get_m3u8_ts(m3u8: M3U8) -> list[str]:
    return [f"{m3u8.base_uri}{f}" for f in m3u8.files]


async def download_m3u8_v_async(ctx: Context, m3u8_u: str, filepath: str, con_num=10, exist_m3u8=False) -> Error:
    if ctx.timeoutd():
        return TIMEOUT

    m3u8_f = get_file_path(filepath, M3u8FName)
    logger.info(f"save to {m3u8_f}")
    if exist_m3u8:
        m3u8 = load(m3u8_f, timeout=ctx.remain_sec())
    else:
        m3u8 = save_m3u8(m3u8_u, m3u8_f, timeout=ctx.remain_sec())
        if not m3u8:
            logger.error(f"download_m3u8_v_async load m3u8 err")
            return NO_M3U8

    if ctx.timeoutd():
        return TIMEOUT

    tasks = []
    ts_fs = []
    for u in _get_m3u8_ts(m3u8):
        ts_f = get_file_path(filepath, url_f_name(u))
        if check_file_exist(ts_f):
            logger.debug(f"download_v_async {ts_f} exist")
            continue
        ts_fs.append(ts_f)
        tasks.append(async_download(u, ts_f, timeout=ctx.remain_sec()))

    logger.info(f"download_v_async start {len(tasks)}")
    result: list[Error] = await con_async(tasks, con_num=con_num)
    errs = check_errors(result)
    if errs:
        logger.error(f"download_v_async fail {errs}, will del")
        for i in errs:
            rm_file(ts_fs[i])
        return NO_TS
    return OK


def download_m3u8_v(ctx: Context, m3u8_u: str, filepath: str, con_num=10, exist_m3u8=False) -> Error:
    return call_async(download_m3u8_v_async(ctx, m3u8_u, filepath, con_num, exist_m3u8))


def merge_m3u8_ts(ctx: Context, m3u8_dir: str) -> Error:
    m3u8_dir = os.path.abspath(m3u8_dir)
    logger.info(f"merge_ts {m3u8_dir}")
    m3u8_f = get_file_path(m3u8_dir, M3u8FName)
    if not check_file_exist(m3u8_f):
        logger.error(f"{m3u8_dir} no m3u8")
        return NO_M3U8

    m3u8 = load(m3u8_f, timeout=ctx.remain_sec())
    for name in m3u8.files:
        f = get_file_path(m3u8_dir, name)
        if not is_binary_f(f):
            logger.error(f"merge_m3u8_ts  will del {f} for not binary")
            rm_file(f)
            return NO_TS
        if not check_file_exist(f):
            logger.info(f"merge no {f}, do nothing")
            return NO_TS

    mp4_f, err = _merge_local_m3u8(m3u8_dir)
    if not err.ok:
        logger.error(f"merge err {m3u8_dir} {err}")
        return TRANS_MP4

    logger.info(f"merge ok {m3u8_dir}")
    logger.info(f"move to {m3u8_dir}")
    move_file(mp4_f, get_path_parent(m3u8_dir))

    rm_m3u8_dir(m3u8_dir)
    return OK


def rm_m3u8_dir(m3u8_dir: str):
    mp4f = get_file_path(get_path_parent(m3u8_dir), f"{get_path_last_part(m3u8_dir)}.mp4")
    if not check_file_exist(mp4f):
        logger.info(f"no {mp4f}, do nothing")
        return
    logger.info(f"del {m3u8_dir}")
    rm_dirs(m3u8_dir)
