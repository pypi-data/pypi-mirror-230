from unittest import TestCase


class TestServiceBase(TestCase):
    def _init(self):
        from utils.server import init_before_server
        from multiprocessing import Queue
        init_before_server("../config.yaml", Queue(), Queue())
        if hasattr(self, "service_name"):
            import grpc
            from grpc_testing import server_from_dictionary, strict_real_time
            self.server = server_from_dictionary(
                {self.pb.DESCRIPTOR.services_by_name[self.service_name]: self.service},
                strict_real_time()
            )

    def _get_res(self, req, method_name):
        method = self.server.invoke_unary_unary(
            method_descriptor=self.pb.DESCRIPTOR.services_by_name[self.service_name].methods_by_name[method_name],
            invocation_metadata={},
            request=req, timeout=300
        )
        # res, metadata, code, _ = method.termination()
        return method.termination()

    def _status_ok_flag(self, status):
        return status.code == "" and status.message == ""

    def _status_ok(self, status, check_code=False):
        if check_code:
            f1 = "check_code"
            f2 = "check_desc"
        else:
            f1 = "code"
            f2 = "message"
        v1 = getattr(status, f1, None)
        v2 = getattr(status, f2, None)
        if v1 is None or v1 != "":
            self.fail(f"!!!_status_ok {f1}={v1} {f2}={v2}")
        if v2 is None or v2 != "":
            self.fail(f"!!!_status_ok {f1}={v1} {f2}={v2}")

    def _code_ok(self, code):
        self.assertIs(code, grpc.StatusCode.OK)
