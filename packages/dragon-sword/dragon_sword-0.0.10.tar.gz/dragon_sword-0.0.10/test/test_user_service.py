from common import TestServiceBase
from gservices import user_pb2 as pb


class TestUserService(TestServiceBase):
    def setUp(self) -> None:
        from gservices.user_service import UserService

        self.service_name = "UserService"
        self.pb = pb
        self.service = UserService()
        self._init()

        self._user_name = "admin"

    def _sign_up(self):
        req = pb.SignupReq(user=self._user_name, passwd="admin123")
        return self._get_res(req, "Signup")

    def test_signup(self):
        res, _, code, _ = self._sign_up()
        self.assertIsInstance(res, pb.SignupRes)
        self._status_ok(res)
        self._code_ok(code)
        self.assertEqual(len(res.token), 80)

    def test_signup_err(self):
        req = pb.SignupReq(user=self._user_name, passwd="err_passwd")
        res, _, code, _ = self._get_res(req, "Signup")
        self._code_ok(code)
        self.assertIsInstance(res, pb.SignupRes)
        self.assertEqual(res.code, "ERR_USER_PWD")
        self.assertEqual(res.message, "用户名或密码错误，请确认用户名或密码")
        self.assertEqual(res.token, "")

    def test_VerifyUser(self):
        res, _, _, _ = self._sign_up()
        token = res.token
        req = pb.VerifyUserReq(token=token)
        res, _, code, _ = self._get_res(req, "VerifyUser")
        self.assertIsInstance(res, pb.VerifyUserRes)
        self._status_ok(res)
        self._code_ok(code)
        self.assertEqual(res.user, self._user_name)

    def test_VerifyUser_err(self):
        req = pb.VerifyUserReq(token="err_token")
        res, _, code, _ = self._get_res(req, "VerifyUser")
        self._code_ok(code)
        self.assertIsInstance(res, pb.VerifyUserRes)
        self.assertEqual(res.code, "ERR_TOKEN_B64_DECODE")
        self.assertEqual(res.message, "token无法base64解码")
        self.assertEqual(res.user, "")

    def test_Access(self):
        res, _, _, _ = self._sign_up()
        token = res.token
        req = pb.AccessReq(token=token)
        res, _, code, _ = self._get_res(req, "Access")
        self._code_ok(code)
        self.assertIsInstance(res, pb.AccessRes)
        self._status_ok(res)
        # self.assertTrue(len(res.projects) > 0)
