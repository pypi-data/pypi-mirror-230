from typing import Callable, Optional

from m3u8 import M3U8, load, Segment

from utils.async_req import url_f_name
from utils.crawler.web import _Web
from utils.data import decode_gzip, decode_bytes, get_ints_in_str
from utils.errno import Error, WEB_ELEMENT, TIMEOUT
from utils.file import (
    get_file_path, dump_f, get_path_last_part,
    check_file_exist, dump_b_f, filename_in_dir,
)
from utils.log import logger
from utils.media.m3u8 import M3u8FName, merge_m3u8_ts
from utils.time import TimeRecord
from utils.server import Context
from .config import Conf


class WebM3u8ByReq(_Web):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _save_m3u8(m3u8_dir, req, m3u8_filter) -> Optional[M3U8]:
        req_u = req.url
        res_body = req.response.body
        if not m3u8_filter(req_u):
            return None
        m3u8 = decode_gzip(res_body)
        m3u8, ok = decode_bytes(m3u8)
        if not ok:
            return None
        m3u8_f_path = get_file_path(m3u8_dir, M3u8FName)
        logger.info(f"save m3u8 {m3u8_f_path}")
        dump_f(m3u8_f_path, m3u8)
        return load(m3u8_f_path)

    @staticmethod
    def _save_ts(m3u8_dir, req, ts_filter) -> Optional[str]:
        req_u = req.url
        res_body = req.response.body
        if not ts_filter(req_u):
            return None
        f_name = url_f_name(req_u)
        f_path = get_file_path(m3u8_dir, f_name)

        log_f_path = get_file_path(get_path_last_part(m3u8_dir), f_name)
        if check_file_exist(f_path):
            logger.debug(f"save_ts {log_f_path} exist, will not re save")
        else:
            logger.debug(f"save_ts {log_f_path}")
            dump_b_f(f_path, decode_gzip(res_body))
        return f_name

    @staticmethod
    def _next_miss_ts(exist_ts, m3u8: M3U8) -> tuple[Optional[Segment], bool]:
        """
        miss ts信息，是否miss
        """
        if not exist_ts:
            return None, True
        if not m3u8:
            return None, True

        for item in m3u8.segments:
            if item.uri in exist_ts:
                continue
            return item, True
        return None, False

    def _forward(self, curr_ts_name: str, miss_ts: Segment, forward_xpath: str,
                 forward_tr: TimeRecord, forward_step_sec=10):
        """
        视频前进
        """
        if not forward_tr.gap_up_to(60):
            # logger.info(f"forward interval not enough {get_now_stamp() - last_forward_stamp}")
            return
        if curr_ts_name is None or not miss_ts:
            # logger.info(f"forward no {curr_ts_name} {miss_ts}")
            return

        ts_duration = miss_ts.duration
        miss_ts_name = miss_ts.uri
        sec = (get_ints_in_str(miss_ts_name)[0] - get_ints_in_str(curr_ts_name)[0]) * ts_duration
        sec = int(sec)
        # logger.info(f"forward compute {miss_ts_name} {curr_ts_name} {sec}")
        # 最少间隔多少分钟，才去快进
        if sec <= 2 * 60:
            return

        forward_tr.record()
        # 留出1分钟，做超时buffer
        num = (sec - 1 * 60) / forward_step_sec
        num = int(num)
        logger.info(f"forward {miss_ts_name} {curr_ts_name} {sec} {num}")
        for i in range(num):
            if not forward_xpath or not self.click(forward_xpath, timeout=3).ok:
                self.press_keyboard(1)
        return

    def download_ts(self, m3u8_dir: str,
                    m3u8_filter: Callable, ts_filter: Callable,
                    play_xpath: str,
                    forward_xpath: str = None,
                    ctx: Context = Context(Conf.timeout)
                    ) -> Error:
        if ctx.timeoutd():
            return TIMEOUT

        if not self.click(play_xpath, timeout=ctx.remain_sec()).ok:
            logger.error(f"download_ts {get_path_last_part(m3u8_dir)} cant play")
            return WEB_ELEMENT

        exist_ts_names = {item for item in filename_in_dir(m3u8_dir) if ts_filter(item)}

        visited_u = set()
        download_tr = TimeRecord()
        forward_tr = TimeRecord()
        curr_ts_name: Optional[str] = None
        m3u8: Optional[M3U8] = None

        logger.info(f"download_ts {get_path_last_part(m3u8_dir)}")
        while True:
            if download_tr.gap_up_to(10 * 60):
                logger.info(f"download_ts timeout {get_path_last_part(m3u8_dir)}")
                return TIMEOUT
            miss_ts, miss = self._next_miss_ts(exist_ts_names, m3u8)
            if not miss:
                logger.info(f"download_ts {m3u8_dir} all done")
                break

            exist_num = 0
            self._forward(curr_ts_name, miss_ts, forward_xpath, forward_tr)

            # 无法中断？
            for req in self.driver.requests:
                if exist_num >= 10 and m3u8 is not None:
                    logger.info(f"download_ts exist {exist_num} >= 10, break")
                    break
                if req.response and req.url not in visited_u:
                    visited_u.add(req.url)
                    # 保存m3u8文件
                    _m3u8 = self._save_m3u8(m3u8_dir, req, m3u8_filter)
                    if _m3u8 is not None:
                        m3u8 = _m3u8
                        download_tr.record()
                        continue

                    # 保存ts文件
                    ts_name = self._save_ts(m3u8_dir, req, ts_filter)
                    if ts_name is not None:
                        if ts_name in exist_ts_names:
                            exist_num += 1
                        else:
                            exist_ts_names.add(ts_name)
                        download_tr.record()
                        curr_ts_name = self._max_ts_name(curr_ts_name, ts_name, m3u8)
        return merge_m3u8_ts(ctx, m3u8_dir)

    @staticmethod
    def _max_ts_name(curr: str, new: str, m3u8: Optional[M3U8]) -> str:
        if m3u8 is None:
            return curr
        files = m3u8.files
        if new not in files:
            return curr
        if curr not in files:
            return new
        return files[max(files.index(curr), files.index(new))]
