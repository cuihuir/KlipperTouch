import pytest

from klippertouch.moonraker.safety import CommandPolicy, UnsafeCommandError


def test_read_only_policy_allows_get_endpoints() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "server/info")
    policy.validate_http("GET", "printer/info")
    policy.validate_http("GET", "printer/objects/list")


def test_read_only_policy_allows_query_endpoint() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "printer/objects/query")


def test_read_only_policy_allows_file_list_endpoint() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "server/files/list")


def test_read_only_policy_allows_file_metadata_endpoint() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "server/files/metadata")


def test_read_only_policy_allows_update_status_endpoint() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "machine/update/status")


def test_read_only_policy_allows_temperature_store_endpoint() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "server/temperature_store")


def test_read_only_policy_normalizes_endpoint_slashes() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_http("GET", "/server/info/")


def test_read_only_policy_blocks_non_get_requests() -> None:
    policy = CommandPolicy(read_only=True)
    with pytest.raises(UnsafeCommandError):
        policy.validate_http("POST", "server/info")


def test_read_only_policy_blocks_unlisted_get_endpoints() -> None:
    policy = CommandPolicy(read_only=True)
    with pytest.raises(UnsafeCommandError):
        policy.validate_http("GET", "printer/gcode/script")


def test_read_only_policy_allows_read_only_jsonrpc_methods() -> None:
    policy = CommandPolicy(read_only=True)
    policy.validate_jsonrpc("printer.objects.query")
    policy.validate_jsonrpc("printer.objects.subscribe")
    policy.validate_jsonrpc("server.info")


def test_read_only_policy_blocks_control_endpoints() -> None:
    policy = CommandPolicy(read_only=True)
    with pytest.raises(UnsafeCommandError):
        policy.validate_jsonrpc("printer.gcode.script")
    with pytest.raises(UnsafeCommandError):
        policy.validate_jsonrpc("printer.print.start")


def test_read_only_policy_blocks_unknown_jsonrpc_methods() -> None:
    policy = CommandPolicy(read_only=True)
    with pytest.raises(UnsafeCommandError):
        policy.validate_jsonrpc("machine.system_info")


def test_non_read_only_policy_allows_jsonrpc_methods() -> None:
    policy = CommandPolicy(read_only=False)
    policy.validate_jsonrpc("printer.gcode.script")
    policy.validate_jsonrpc("machine.system_info")
