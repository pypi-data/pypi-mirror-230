from utils.auth.token import (
    certify_token, certify_user, Token,
    check_token
)
from utils.time import get_now_stamp_float
from common import TestServiceBase


class TestUtilsAuthToken(TestServiceBase):
    def test_generate_token(self):
        from utils.time import get_now_stamp_float
        name = "test"
        now = get_now_stamp_float()
        t1 = Token()
        t1.generate(name, now)
        t2 = Token()
        t2.generate(name, now)
        self.assertEqual(len(t1.token), 80)
        self.assertEqual(len(t2.token), 80)
        self.assertEqual(t1.token, t2.token)

    def _get_token(self):
        name = "test"
        now = get_now_stamp_float()
        t = Token()
        t.generate(name, now)
        return t.token

    def test_certify_token_en(self):
        t = Token()
        t.generate("public", get_now_stamp_float())

        token = t.token
        self.assertTrue(certify_token(token))

    def test_certify_token_int(self):
        self.assertFalse(certify_token("1234"))

    def test_certify_token_int_space(self):
        self.assertFalse(certify_token("1234 123"))

    def test_certify_token_empty(self):
        self.assertFalse(certify_token(""))

    def test_certify_vip(self):
        t = Token()
        t.generate("admin", get_now_stamp_float())
        self.assertTrue(certify_token(t.token))

    def test_certify_no_user(self):
        t = Token()
        t.generate("no_user", get_now_stamp_float())
        self.assertFalse(certify_token(t.token))

    def test_certify_token_zh(self):
        self.assertFalse(certify_token("测试"))

    def test_certify_token_zh_mix(self):
        self.assertFalse(certify_token("测试123"))

    def test_certify_token_zh_mix2(self):
        self.assertFalse(certify_token("测试 123 "))

    def test_certify_token_zh_mix3(self):
        self.assertFalse(certify_token("测试 123 xxs 1x"))

    def test_certify_token_expire(self):
        from utils.time import parse_time_str, get_timestamp
        t = Token()
        t.generate("public", get_timestamp(parse_time_str("2023-01-01 13:01:01")))

        self.assertFalse(certify_token(t.token))

    def test_certify_user(self):
        token, err = certify_user("public", "12345678")
        self.assertEqual(err.desc, "")
        self.assertEqual(len(token), 80)

    def test_certify_vip_user(self):
        token, err = certify_user("admin", "admin123")
        self.assertEqual(err.desc, "")
        self.assertEqual(len(token), 80)

    def test_certify_user_vip_pwd_err(self):
        token, err = certify_user("admin", "err_pwd")
        self.assertIs(token, "")
        self.assertEqual(err.desc, "用户名或密码错误，请确认用户名或密码")

    def test_certify_user_no_user(self):
        token, err = certify_user("no_user", "12345678")
        self.assertIs(token, "")
        self.assertEqual(err.desc, "用户名或密码错误，请确认用户名或密码")

    def test_certify_user_err_pwd(self):
        token, err = certify_user("public", "err_pwd")
        self.assertIs(token, "")
        self.assertEqual(err.desc, "用户名或密码错误，请确认用户名或密码")

    def test_Token_parse(self):
        now = get_now_stamp_float()
        name = "test"
        t1 = Token()
        t1.generate(name, now)

        t2 = Token()
        _, _, err = t2.parse(t1.token)
        self.assertTrue(err.ok)

        self.assertEqual(t1.token, t2.token)
        self.assertEqual(t1.t_str, t2.t_str)
        self.assertEqual(t1.name_sha, t2.name_sha)

    def test_Token_filter_user_no_user(self):
        t = Token()
        t.generate("test", get_now_stamp_float())
        user, err = t.filter_user([""])
        self.assertEqual(user, "")
        self.assertFalse(err.ok)

    def test_check_token(self):
        token, err = certify_user("public", "12345678")
        self.assertTrue(err.ok)
        err = check_token(token)
        self.assertTrue(err.ok)

    def test_check_token_empty(self):
        err = check_token("")
        self.assertEqual(err.desc, "token不存在")

    def test_check_token_not_valid(self):
        err = check_token("err_token")
        self.assertEqual(err.desc, "token失效")
