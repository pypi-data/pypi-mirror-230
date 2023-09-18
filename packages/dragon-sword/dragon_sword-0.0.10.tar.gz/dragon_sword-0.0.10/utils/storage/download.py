from utils.file import get_file_path, check_path_exist, move_file_in_dir, f_other_format, rename_f


class FileStorage:
    def __init__(self, name: str, s_dir: str):
        self._name = name
        self._dir = s_dir

    @property
    def tmp_path(self) -> str:
        return get_file_path(self._dir, f"downloading_{self._name}")

    @property
    def final_path(self) -> str:
        return get_file_path(self._dir, f"{self._name}")

    def download_path(self, name: str) -> str:
        return get_file_path(self.tmp_path, name)

    def exist_f(self, name: str) -> str:
        """
        检查临时和最终下载目录是否存在文件
        """
        for _path in (self.final_path, self.tmp_path):
            f_path = get_file_path(_path, name)
            if check_path_exist(f_path):
                return f_path
        return ""

    def move_to_final(self):
        move_file_in_dir(self.tmp_path, self.final_path)

    def rename_with_suffix(self, ori_name, name, suffix):
        for _format in suffix:
            ori_name = f_other_format(ori_name, _format)
            name = f_other_format(name, _format)

            for _path in (self.final_path, self.tmp_path):
                ori_path = get_file_path(_path, ori_name)

                if check_path_exist(ori_path):
                    name_path = get_file_path(_path, name)
                    # logger.info(f"rename {ori_path} to {name_path}")
                    rename_f(ori_path, name_path)
