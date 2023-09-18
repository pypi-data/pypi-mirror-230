from multiprocessing import Queue
from utils.errno import Error, OK


def init_base(conf_path: str = None, log: Queue = None, qs=None, global_conf=None, log_f_prefix: str = "") -> Error:
    from utils.log import logger
    if global_conf:
        from utils.config import init_global_conf
        init_global_conf(global_conf)
    elif conf_path:
        from utils.config import init_conf
        err = init_conf(conf_path, log_f_prefix)
        if not err.ok:
            logger.error(f"{conf_path} init {err}")
            return err

    from utils.log.q import QLogM
    if log:
        QLogM.init_q(log)
    from utils.log.log import init
    from utils.config import log_conf
    init(log_conf())

    from .q import QM
    if qs:
        QM.init(qs)
    return OK
