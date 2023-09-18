from unittest import TestCase
from utils.auth.auth import AuthM
from utils.auth.errno import USER_EMPTY, USER_PWD
from test.common import TestServiceBase


class Test_CookAuthM(TestServiceBase):
    def test_check_user_passwd(self):
        err = AuthM.check_user_passwd("admin", "12345678")
        self.assertTrue(err.ok)
        err = AuthM.check_user_passwd("public", "12345678")
        self.assertTrue(err.ok)

    def test_check_no_user(self):
        err = AuthM.check_user_passwd("not_exist", "password")
        self.assertFalse(err.ok)
        self.assertIs(err, USER_EMPTY)

    def test_check_user_passwd_err(self):
        err = AuthM.check_user_passwd("admin", "err_password")
        self.assertFalse(err.ok)
        self.assertIs(err, USER_PWD)
