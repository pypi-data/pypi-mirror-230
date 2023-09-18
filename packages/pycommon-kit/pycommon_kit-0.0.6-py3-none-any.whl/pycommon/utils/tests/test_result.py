from pycommon.utils.result import Result


def get_success_result() -> Result:
    return Result.success("success_data")


def get_failure_result() -> Result:
    return Result.failure("test_error")


def get_server_error_result() -> Result:
    return Result.server_error("test_server_error")


class TestResult:
    def __init__(self) -> None:
        self.success_result = get_success_result()
        self.failure_result = get_failure_result()
        self.server_error_result = get_server_error_result()

    def test_success_result(self) -> None:
        assert self.success_result.is_success() is True
        assert self.success_result.is_failure() is False
        assert self.success_result.error is None
        assert self.success_result.data == "success_data"
        assert self.success_result.status == "success"

    def test_failure_result(self) -> None:
        assert self.success_result.is_success() is False
        assert self.success_result.is_failure() is True
        assert self.success_result.data is None
        assert self.success_result.error == "test_error"
        assert self.success_result.status == "failure"

    def test_server_error_result(self) -> None:
        assert self.success_result.is_success() is False
        assert self.success_result.is_failure() is True
        assert self.success_result.data is None
        assert self.success_result.error == "test_server_error"
        assert self.success_result.status == "failure"
