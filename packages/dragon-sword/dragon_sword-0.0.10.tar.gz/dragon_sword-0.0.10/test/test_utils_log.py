import os
from unittest import TestCase

from utils.log import log
from utils.log import logger


class Test(TestCase):
    def setUp(self) -> None:
        from utils.config import _init_conf, log_conf
        from io import StringIO
        f = StringIO()
        _log_conf = """
        log:
          - writer: file
            level: info
            formatter: ""
            writer_config:
              filename: "test_utils_log.log"
              log_path: ""
              max_size: 0
              max_backups: 10
              max_age: midnight
              compress: False
            format_config:
              time_fmt: ""
              fmt: ""
          - writer: console
            level: info
            formatter: ""
        """
        f.write(_log_conf)
        f.seek(0)
        c, _ = _init_conf(f)
        f.close()
        log.init(log_conf())

    def test_info(self):
        logger.info(f"single test_info is ok {os.getpid()}")

    # def test_mp_info(self):
    #     def _log(i):
    #         logger.info(f"{i} {random.random()} mp test_info is ok {os.getpid()}")
    #     ps = [Process(target=_log, args=(i, ))for i in range(3)]
    #     [p.start() for p in ps]
    #     [p.join() for p in ps]

