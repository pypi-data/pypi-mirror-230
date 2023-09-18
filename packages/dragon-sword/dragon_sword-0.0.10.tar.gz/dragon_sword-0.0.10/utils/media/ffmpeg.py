import os

from utils.errno import Error, OK, TRANS_MP4, DOWNLOAD
from utils.file import get_path_last_part, get_file_path, check_file_exist
from utils.log import logger
from utils.system import run_cmd


def _ffmpeg_base(in_path, out_path) -> list[str]:
    return ["ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-allowed_extensions", "ALL",
            "-i", in_path,
            "-c", "copy", out_path]


def extract_pcm(file_path: str, out: str):
    cmd = _ffmpeg_base(file_path, out)
    cmd.extend(["-f", "s16le", "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000"])
    out, success = run_cmd(cmd)
    return success


def download_m3u8_with(u: str, filepath: str, refer) -> Error:
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    cmd = (f'ffmpeg -hide_banner -i {u}'
           f' -user_agent "{user_agent}"'
           f' -headers "Referer: {refer}"'
           f' -headers "Accept: */*"'
           f' -headers "Accept-Encoding: gzip, deflate, br"'
           f' -headers "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7"'
           f' -headers "Cache-Control: no-cache"'
           f' -headers "Origin: {refer}"'
           f' -headers "Pragma: no-cache"'
           f''' -headers 'Sec-Ch-Ua: "Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"' '''
           f' -headers "Sec-Ch-Ua-Mobile: ?0"'
           f' -headers "Sec-Ch-Ua-Platform: "Linux""'
           f' -headers "Sec-Fetch-Dest: empty"'
           f' -headers "Sec-Fetch-Mode: cors"'
           f' -headers "Sec-Fetch-Site: cross-site"'
           # f' -headers "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"'
           # f' -headers '
           # f' -headers '
           # f' -headers '
           f' {filepath}'
           )
    logger.info(cmd)
    r = os.system(cmd)
    logger.info(f"{r}")
    return OK


def download_m3u8(u: str, filepath: str) -> Error:
    cmd = _ffmpeg_base(u, filepath)
    out, success = run_cmd(cmd)
    if not success:
        return DOWNLOAD
    return OK


def _merge_local_m3u8(_dir, m3u8_name="index.m3u8", filename=None) -> tuple[str, Error]:
    """
    不要直接使用，使用.m3u8.merge_m3u8_ts
    """
    if not filename:
        filename = get_path_last_part(_dir)

    mp4_f = get_file_path(_dir, f"{filename}.mp4")
    if check_file_exist(mp4_f):
        logger.info(f"merge_local_m3u8 do nothing {mp4_f} exist")
        return mp4_f, OK

    cmd = _ffmpeg_base(get_file_path(_dir, m3u8_name), mp4_f)
    out, success = run_cmd(cmd)
    if not success:
        return mp4_f, TRANS_MP4
    return mp4_f, OK


def trans_to_mp4(_input: str, output: str) -> Error:
    cmd = _ffmpeg_base(_input, output)
    out, success = run_cmd(cmd)
    if not success:
        return TRANS_MP4
    return OK
