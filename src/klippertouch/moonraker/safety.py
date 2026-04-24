class UnsafeCommandError(RuntimeError):
    pass


class CommandPolicy:
    def __init__(self, read_only: bool = True) -> None:
        self.read_only = read_only
        self.allowed_gets = {
            "server/info",
            "server/files/list",
            "server/temperature_store",
            "machine/update/status",
            "printer/info",
            "printer/objects/list",
            "printer/objects/query",
        }
        self.allowed_jsonrpc_methods = {
            "printer.objects.query",
            "printer.objects.subscribe",
            "server.info",
        }

    def validate_http(self, method: str, endpoint: str) -> None:
        normalized = endpoint.strip("/")
        if self.read_only and method.upper() != "GET":
            raise UnsafeCommandError(
                f"Blocked non-GET request in read-only mode: {method} {endpoint}"
            )
        if self.read_only and normalized not in self.allowed_gets:
            raise UnsafeCommandError(f"Blocked endpoint in read-only mode: {endpoint}")

    def validate_jsonrpc(self, method: str) -> None:
        if not self.read_only:
            return
        if method not in self.allowed_jsonrpc_methods:
            raise UnsafeCommandError(f"Blocked JSON-RPC method in read-only mode: {method}")
