from multiprocessing import Queue

from utils.data import uniq_id
from utils.file import get_file_path, load_f_line, dump_f_lines, dump_f, append_f_line
from utils.log import logger
from utils.server import QM


class FileMQ:
    def __init__(self, name: str, record_dir: str):
        self._name = name
        self._record_dir = record_dir
        self._q_name = f"task_{self._name}_{uniq_id()}_q"

    def init(self):
        QM.register_q(self._q_name, Queue(1))

    def _todo_path(self) -> str:
        return get_file_path(self._record_dir, f"todo_{self._name}.txt")

    def _ing_path(self) -> str:
        return get_file_path(self._record_dir, f"ing_{self._name}.txt")

    def _done_path(self) -> str:
        return get_file_path(self._record_dir, f"done_{self._name}.txt")

    def _merge_record(self):
        """
        todo里去掉done，ing去掉done
        todo都挪到ing
        todo清空
        :return:
        """
        dones, _ = load_f_line(self._done_path())
        dones = set(dones)
        logger.debug(f"dones num={len(dones)}")

        todos, _ = load_f_line(self._todo_path())
        todos = set(todos)
        todos.difference_update(dones)
        logger.debug(f"todos num={len(todos)}")

        ing_s, _ = load_f_line(self._ing_path())
        ing_s = set(ing_s)

        new_todos = todos
        new_todos.difference_update(ing_s)
        logger.debug(f"new todos num={len(new_todos)}")

        ing_s.update(todos)
        ing_s.difference_update(dones)
        logger.debug(f"ing_s num={len(ing_s)}")

        dump_f_lines(self._ing_path(), list(ing_s))
        dump_f(self._todo_path(), "")

        return new_todos

    def push_todo(self):
        self._merge_record()
        lines, _ = load_f_line(self._ing_path())
        for t in lines:
            QM.add_task(self._q_name, t.strip())

    def get_a_todo(self):
        u, _ = QM.get_a_task(self._q_name)
        return u

    def record_done(self, u: str):
        append_f_line(self._done_path(), u)
