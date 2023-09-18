from typing import Callable

from requests import Session

from utils.crawler.web import _Web
from utils.errno import Error, OK, NO_M3U8, TIMEOUT, WEB_ELEMENT
from utils.file import get_path_parent
from utils.log import logger
from utils.media.m3u8 import download_m3u8_v, merge_m3u8_ts
from utils.server import Context
from .config import Conf


class WebM3u8ByUrl(_Web):
    def __init__(self):
        super().__init__()
        self._req_session = Session()

    def __del__(self):
        super().__del__()
        self._req_session.close()

    def _get_m3u8_url(self, ctx: Context, m3u8_filter: Callable = None) -> tuple[str, Error]:
        if ctx.timeoutd():
            return TIMEOUT

        if m3u8_filter:
            for req in self.driver.requests:
                if not req.response:
                    continue
                if m3u8_filter(req.url):
                    return req.url

        # 一般页面只会有一个<video>
        element, err = self.find_element("//video")
        if not err.ok:
            return "", err
        return element.get_dom_attribute("data-src"), OK

    def download_ts(self, m3u8_dir: str, con_num=3, ctx: Context = Context(Conf.timeout)) -> Error:
        if ctx.timeoutd():
            return TIMEOUT

        m3u8_u, err = self._get_m3u8_url(ctx)
        if not err.ok:
            logger.error(f"download_ts no m3u8_u")
            return NO_M3U8

        if "mp4" in m3u8_u:
            logger.info(f"m3u8 url maybe media {m3u8_u}")
            if self.download_mp4(ctx, m3u8_u, get_path_parent(m3u8_dir)):
                return OK

        logger.info(f"download_ts {m3u8_u}")
        err = download_m3u8_v(ctx, m3u8_u, m3u8_dir, con_num=con_num)
        if not err.ok:
            return err
        return merge_m3u8_ts(ctx, m3u8_dir)
