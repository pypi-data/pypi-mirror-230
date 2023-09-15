import pytest

from egse.control import Failure, Response, Success


def test_failure():

    with pytest.raises(Failure) as failure:
        try:
            raise ValueError("original argument raised a valueError")
        except ValueError as exc:
            raise Failure("Raised a Failure", exc)

    assert isinstance(failure.value, Exception)
    assert isinstance(failure.value, Response)
    assert isinstance(failure.value, Failure)

    assert "original argument" in str(failure.value)

    def func_returns_failure() -> Response:
        return Failure("Something failed", ValueError("Incorrect value"))

    rc = func_returns_failure()

    if rc.successful:
        assert not isinstance(rc, Exception)

    assert isinstance(rc, Failure)
    assert "value" in str(rc)


def test_success():

    def func_returns_success() -> Response:
        return Success("A success story", Success("return code", 42))

    rc = func_returns_success()

    assert isinstance(rc, Success)
    assert isinstance(rc, Response)

    assert "return code" in str(rc)

