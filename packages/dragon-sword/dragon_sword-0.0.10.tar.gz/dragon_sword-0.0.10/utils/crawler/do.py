import random
import time
from typing import Callable

from utils.log import logger
from utils.server import MultiM

from utils.crawler.storage import _Storage
from .web import _Web


def __continue_to_download(web: _Web, storage, u, another_u: Callable, url_loaded: Callable) -> bool:
    # web.get("https://nowsecure.nl")
    # input("Done?")
    if web.goto(u) and (not url_loaded or url_loaded(u)):
        storage.rename(web.ori_page_name(), web.page_name())
        return True

    u_ok = False
    if another_u:
        for _u in another_u(u):
            if web.goto(_u) and (not url_loaded or url_loaded(u)):
                u_ok = True
                break
    if not u_ok:
        logger.info(f"open fail {u} {web.page_name()}")
        return False

    return True


def _get_and_download(storage: _Storage, web_cls, download_v: Callable,
                      anther_u=None, check_url_loaded=False):
    logger.debug(f"_get_and_download {check_url_loaded}")
    web = web_cls()
    web.init()
    url_loaded = None if not check_url_loaded else web.url_loaded
    while True:
        u = storage.get_a_todo()
        if not u:
            time.sleep(3)
            continue
        logger.info(f"_get_and_download {u}")
        if not __continue_to_download(web, storage, u, anther_u, url_loaded):
            time.sleep(random.randint(30, 60))
            continue

        # 检查是否存在，存在跳过，存在还未merge的文件夹，需要继续下载
        if storage.exist_video(f"{web.page_name()}.mp4"):
            logger.info(f"exist {u}")
        # 调用特定的下载逻辑
        elif not download_v(web, storage, web.page_name()):
            logger.error(f"_get_and_download download fail {u}")
            continue
        storage.record_done(u)
        time.sleep(random.randint(0, 3))


def main(site: str, web_cls, download_v, s_dir,
         anther_u=None, check_url_loaded=False, con_site_num=1):
    storage = _Storage(site, s_dir)
    storage.init()
    storage.move_to_final()

    def _push_todo(s: _Storage):
        while True:
            s.push_todo()
            time.sleep(10)

    MultiM.add_p(f"{site}-push-todo", _push_todo, storage)
    for i in range(con_site_num):
        MultiM.add_p(f"{site}-{i}-download",
                     _get_and_download,
                     storage, web_cls,
                     download_v, anther_u,
                     check_url_loaded)
