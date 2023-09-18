import traceback
from typing import Optional

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.undetected_chromedriver.v2 import Chrome

from utils.async_req import url_f_name, async_download
from utils.crawler.config import Conf
from utils.data import format_file_name
from utils.errno import Error, OK, INTERVAL_SERVER, WEB_ELEMENT
from utils.log import logger
from utils.system import is_win
from utils.file import get_file_path, is_binary_f, rm_file, move_file
from utils.call import call_async
from utils.server import Context


# from undetected_chromedriver import Chrome
# from seleniumwire.undetected_chromedriver.v2 import ChromeOptions


class _Web:
    def __init__(self):
        super().__init__()
        self.driver: Chrome

    def init(self):
        self.driver = self._new_uc_driver()

    @staticmethod
    def copy():
        web = _Web()
        web.init()
        return web

    @staticmethod
    def _proxy() -> str:
        if is_win():
            proxy = "http://127.0.0.1:51837"
        else:
            proxy = "http://127.0.0.1:7890"
        return proxy

    def _new_uc_driver(self) -> Chrome:
        options = ChromeOptions()
        options.add_argument("--mute-audio")

        wire_options = {}
        if self._proxy():
            # 会被wire默认设置覆盖,wire应该是自己起了一个代理服务器抓请求
            wire_options = {
                'proxy': {
                    'http': self._proxy(),
                    'https': self._proxy(),
                    'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
                }
            }
        # 忽略wire的无用日志
        # import logging
        # logging.getLogger("seleniumwire.handler").setLevel(logging.ERROR)
        # logging.getLogger("seleniumwire.server").setLevel(logging.ERROR)
        driver = Chrome(
            seleniumwire_options=wire_options,
            options=options,
            headless=Conf.headless,
            use_subprocess=False,
            driver_executable_path="./bin/chromedriver-linux64/chromedriver",
            # browser_executable_path="./bin/chrome-linux64/chrome"
        )
        return driver

    def clear(self):
        del self.driver.requests
        logger.info("Web requests cleared")

    def goto(self, u: str) -> bool:
        self.clear()
        from selenium.common.exceptions import WebDriverException
        try:
            self.driver.get(u)
        except WebDriverException as e:
            logger.info(f"!!!get {u} {e}")
            return False
        # dump_f("records/tmp.html", self.driver.page_source)
        return True

    def ori_page_name(self):
        return self.driver.title.replace("|", "_").replace("/", "").replace("\\", "")

    def page_name(self) -> str:
        name = self.ori_page_name()
        return format_file_name(name)

    def url_loaded(self, u: str) -> bool:
        """
        通过url的最后一部分，是否在标题中判断
        :param u:
        :return:
        """
        name = url_f_name(u)
        page_name = self.page_name()
        return name in page_name or name.upper() in page_name

    def find_element(self, value, by=By.XPATH) -> tuple[Optional[WebElement], Error]:
        try:
            return self.driver.find_element(by=by, value=value), OK
        except NoSuchElementException:
            logger.info(f"find_element {traceback.format_exc()}")
            return None, WEB_ELEMENT

    def get_element_content(self, value, by=By.XPATH, attr="src") -> str:
        element, err = self.find_element(value, by)
        if not err.ok:
            return ""
        return element.get_dom_attribute(attr)

    def find_elements(self, value, by=By.XPATH) -> tuple[list[WebElement], Error]:
        try:
            return self.driver.find_element(by=by, value=value), OK
        except NoSuchElementException:
            logger.info(f"find_elements {traceback.format_exc()}")
            return [], WEB_ELEMENT

    def get_elements_content(self, value, by=By.XPATH, attr="src") -> list[str]:
        es, err = self.find_elements(value, by)
        if not err.ok:
            return []
        return [e.get_dom_attribute(attr) for e in es]

    def wait_element(self, value, by=By.XPATH, need_click=False, timeout=15):
        if need_click:
            cond = expected_conditions.element_to_be_clickable((by, value))
        else:
            cond = expected_conditions.presence_of_element_located((by, value))
        try:
            return WebDriverWait(self.driver, timeout, poll_frequency=0.1).until(cond)
        except TimeoutException:
            return None

    def go_to_iframe(self, xpath="//iframe") -> Error:
        iframe = self.wait_element(xpath)
        if not iframe:
            return INTERVAL_SERVER
        iframe_u = iframe.get_dom_attribute("src")
        logger.info(f"go to iframe {iframe_u}")
        self.goto(iframe_u)
        return OK

    def click(self, xpath, timeout=15):
        btn = self.wait_element(xpath, need_click=True, timeout=timeout)
        if not btn:
            return INTERVAL_SERVER
        try:
            btn.click()
        except ElementClickInterceptedException as e:
            logger.info(f"wait_element {xpath} err={e}")
            return INTERVAL_SERVER
        # btn.send_keys(Keys.ENTER)
        return OK

    def press_keyboard(self, num):
        actions = ActionChains(self.driver)
        for i in range(num):
            actions.send_keys(Keys.ARROW_RIGHT)
        actions.perform()

    def download_mp4(self, ctx: Context, u: str, s_dir: str) -> bool:
        f_path = get_file_path(s_dir, url_f_name(u))
        err = call_async(async_download(u, f_path, timeout=ctx.remain_sec()))
        if not err.ok or not is_binary_f(f_path):
            rm_file(f_path)
            return False
        move_file(f_path, get_file_path(s_dir, f"{self.page_name()}.mp4"))
        return True

    def _exit(self):
        if hasattr(self, "driver"):
            self.driver.quit()
            logger.info(f"close driver")

    def __del__(self):
        self._exit()
