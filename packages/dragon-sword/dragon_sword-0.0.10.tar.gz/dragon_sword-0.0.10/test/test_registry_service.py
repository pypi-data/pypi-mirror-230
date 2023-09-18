from common import TestServiceBase
from gservices import registry_pb2 as pb


class TestRegistryService(TestServiceBase):
    def setUp(self) -> None:
        from gservices.registry_service import RegistryService
        self.service_name = "RegistryService"
        self.pb = pb
        self.service = RegistryService()
        self._init()

    def test_register(self):
        req = pb.RegisterReq()
        res, _, code, _ = self._get_res(req, "Register")
        # TODO: fail, why?
        # self.assertIsInstance(res, pb.RegisterRes)
        self._status_ok(res)
        self._code_ok(code)

    def test_Instances(self):
        req = pb.InstancesReq()
        res, _, code, _ = self._get_res(req, "Instances")
        # self.assertIsInstance(res, pb.InstancesRes)
        self._status_ok(res)
        self._code_ok(code)
        self.assertTrue(len(res.instances) > 0)

    def test_RegistryCli_get_instance(self):
        from gservices.registry_cli import RegistryCli
        services, err = RegistryCli.get_instance("", {
            "cooker_name": {"AI"}
        })
        print(err)
        self.assertTrue(err.ok)
        services = list(services)
        services.sort()

        # self.assertEqual(len(services), 2)
        # self.assertEqual(services[0].ip, "10.5.32.183")
        # self.assertEqual(services[0].port, "9004")
        #
        # self.assertEqual(services[1].ip, "10.5.32.204")
        # self.assertEqual(services[1].port, "9004")
        services, err = RegistryCli.get_instance("", {
            "cooker_name": {"Houdini", "Gaea"}
        })
        services = list(services)
        services.sort()
        self.assertTrue(err.ok)
        # self.assertEqual(services[0].ip, "10.5.32.204")
        self.assertEqual(services[0].port, "9004")
