from multiprocessing import Queue
from queue import Empty
from typing import Any

from utils.log import logger
from .ctx import Context


class _QM:
    def __init__(self):
        super().__init__()
        self._qs: dict[str, Queue] = {}

    def qs(self) -> list:
        r = []
        for name, q in self._qs.items():
            r.append(name)
            r.append(q)
        return r

    def init(self, r):
        for i in range(0, len(r), 2):
            self._qs[r[i]] = r[i+1]

    def register_q(self, name: str, q: Queue):
        if name in self._qs:
            raise Exception(f"QM has {name}")
        self._qs[name] = q

    def empty_task(self):
        self._qs = {name: Queue() for name in self._qs.keys()}

    def _get_q(self, name) -> Queue:
        if name not in self._qs:
            logger.error(f"QM no {name}")
            return None
        return self._qs[name]

    def add_task(self, name, item, timeout=30 * 60):
        q = self._get_q(name)
        if q:
            q.put((item, Context(timeout)))

    def get_task(self, name, block=True) -> type[Any, Context]:
        q = self._get_q(name)
        if not q:
            return None, None

        try:
            item, ctx = q.get(block=block)
        except Empty:
            logger.error(f"QManager get_task {name} empty")
            return None, None
        return item, ctx

    def get_a_task(self, name) -> type[Any, Context]:
        return self.get_task(name, block=False)

    def task_num(self, name) -> int:
        q = self._get_q(name)
        if not q:
            return 0
        return q.qsize()

    def close(self):
        for name, q in self._qs.items():
            q.close()
            q.join_thread()
        print("QM closed")


QM = _QM()
