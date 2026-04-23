import pytest

from klippertouch.moonraker.safety import CommandPolicy, UnsafeCommandError


def test_read_only_policy_allows_get_endpoints() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "server/info")
    policy.validate_http("GET", "printer/info")
    policy.validate_http("GET", "printer/objects/list")


def test_read_only_policy_blocks_control_endpoints() -> None:
    policy = CommandPolicy(read_only=True)
    with pytest.raises(UnsafeCommandError):
        policy.validate_jsonrpc("printer.gcode.script")
    with pytest.raises(UnsafeCommandError):
        policy.validate_jsonrpc("printer.print.start")
