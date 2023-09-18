import time
from common import TestServiceBase


class Test(TestServiceBase):
    def test_(self):
        from gservices.registry_cli import FConLimit
        target = "test_service"
        token, err = FConLimit().acquire(target, "test_client", timeout=1)
        self.assertTrue(err.ok)
        self.assertNotEqual(token, "")
        # print(f"11111 {token}")
        # 续期2秒，只续1秒，后面睡1秒会过期
        err = FConLimit().renew(target, token, 2)
        # print(f"22222 {err}")
        self.assertTrue(err.ok)

        time.sleep(1)

        # 即使是同一个client，没有token，也不行
        token, err = FConLimit().acquire(target, "test_client", timeout=1)
        self.assertFalse(err.ok)
        # 不同client当然也不行
        token, err = FConLimit().acquire(target, "test_client1", timeout=1)
        self.assertFalse(err.ok)
        self.assertEqual(token, "")

        # 让token过期
        time.sleep(3)

        token, err = FConLimit().acquire(target, "test_client2", timeout=1000)
        self.assertTrue(err.ok)
        self.assertNotEqual(token, "")
        # 释放token
        err = FConLimit().release(target, token)
        self.assertTrue(err.ok)

        token, err = FConLimit().acquire(target, "test_client", timeout=1)
        self.assertTrue(err.ok)
        self.assertNotEqual(token, "")
        err = FConLimit().release(target, token)
        self.assertTrue(err.ok)
