from collections import defaultdict

from utils.auth.errno import USER_EMPTY, USER_PWD, PROJ_EMPTY
from utils.config import get_conf, get_default
from utils.data import Cache
from utils.errno import Error, OK

FieldName = "name"
FieldPwd = "pwd"


class _AuthM(Cache):
    def __init__(self):
        super().__init__()
        self._name = "auth"
        # 用户有权限的项目
        self._user_projects: dict[str, set[str]]
        # 公共项目
        self._public_projects: set[str]
        # 所有项目
        self._all_projects: set[str]

        # 普通用户名: 密码集合，不包括vip
        self._user: dict[str, {str}]
        # 项目名: {用户名: 密码}，不包括vip
        self._proj: dict[str, dict[str, str]]
        # VIP用户名和密码
        self._vip: dict[str, str]
        self._all_users: set

    def _load_proj(self, conf):
        # 公共项目
        public_proj = get_default(conf, "public_project", {})
        self._public_projects = set(public_proj)
        self._all_projects = set()
        self._all_projects.update(public_proj)

        # 私有项目
        self._user_projects = defaultdict(set)
        private_proj = get_default(conf, "private_project", {})
        for user, proj in private_proj.items():
            # 用户个人项目
            self._user_projects[user].update(proj)
            self._all_projects.update(proj)
            # 公共项目
            self._user_projects[user].update(public_proj)

    def _get_user_pwd(self, user_pwd) -> tuple[str, str]:
        name = user_pwd[FieldName]
        pwd = str(user_pwd[FieldPwd])
        return name, pwd

    def _load_user(self, conf):
        assert "user" in conf, "no user in auth, check config"

        self._proj = defaultdict(dict)
        self._user = defaultdict(set)
        self._vip = {}
        self._all_users = set()

        users = get_default(conf, "user", {})
        public_user_pwd_s = []
        if "public" in users:
            public_user_pwd_s = users["public"]
            users.pop("public")

        # 项目用户
        for proj, user_pwd_s in users.items():
            for user_pwd in user_pwd_s:
                name, pwd = self._get_user_pwd(user_pwd)
                self._proj[proj][name] = pwd
                self._user[name].add(pwd)
                self._all_users.add(name)

        # 公共用户，包括vip
        for user_pwd in public_user_pwd_s:
            name, pwd = self._get_user_pwd(user_pwd)
            if user_pwd.get("is_vip"):
                self._vip[name] = pwd
            else:
                self._user[name].add(pwd)
            self._all_users.add(name)

    def _load(self):
        config = get_conf(self._name)
        self._load_proj(config)
        self._load_user(config)

    def user_projects(self, user: str, is_vip=False) -> set[str]:
        if is_vip:
            return self.get("_all_projects")
        return self.get("_user_projects").get(user, self._public_projects)

    def check_proj_user_passwd(self, proj: str, user: str, passwd: str) -> Error:
        """
        校验项目+用户名+密码
        :param proj:
        :param user:
        :param passwd:
        :return:
        """
        if proj and proj not in self.get("_proj"):
            return PROJ_EMPTY

        if user in self.get("_proj")[proj]:
            _passwd = self.get("_proj")[proj][user]
        elif user in self.get("_vip"):
            _passwd = self.get("_vip")[user]
        else:
            return USER_EMPTY

        if passwd != _passwd:
            return USER_PWD
        return OK

    def check_user_passwd(self, user: str, passwd: str) -> Error:
        """
        校验用户名和密码
        :param user:
        :param passwd:
        :return:
        """
        if user in self.get("_user"):
            _passwd = self.get("_user")[user]
        elif user in self.get("_vip"):
            _passwd = {self.get("_vip")[user]}
        else:
            return USER_EMPTY

        if passwd not in _passwd:
            return USER_PWD
        return OK

    @property
    def all_users(self) -> set:
        return self.get("_all_users")

    @property
    def vips(self):
        self._init_data()
        return self.get("_vip").keys()

    @property
    def general_users(self):
        self._init_data()
        return self.get("_user").keys()


AuthM = _AuthM()
