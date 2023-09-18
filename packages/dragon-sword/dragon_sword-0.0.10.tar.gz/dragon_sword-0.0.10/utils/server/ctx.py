from utils.time import get_now_stamp, get_stamp_after


class Context:
    def __init__(self, sec: int, start=get_now_stamp()):
        self._start = start
        self._deadline = int(get_stamp_after(self._start, second=sec))
        self.timeout = sec

    def timeoutd(self, now=get_now_stamp()) -> bool:
        return now >= self._deadline

    def remain_sec(self, now=get_now_stamp()) -> int:
        return max(0, self._deadline - now)
