from typing import Any, cast

import requests

from klippertouch.config.models import PrinterConfig
from klippertouch.moonraker.safety import CommandPolicy


class MoonrakerClient:
    def __init__(self, config: PrinterConfig, policy: CommandPolicy | None = None) -> None:
        self.config = config
        self.policy = policy or CommandPolicy(read_only=True)

    @property
    def endpoint(self) -> str:
        proto = "https" if self.config.moonraker_ssl else "http"
        normalized_path = self.config.moonraker_path.strip("/")
        path = f"/{normalized_path}" if normalized_path else ""
        return f"{proto}://{self.config.moonraker_host}:{self.config.moonraker_port}{path}"

    @property
    def websocket_endpoint(self) -> str:
        proto = "wss" if self.config.moonraker_ssl else "ws"
        normalized_path = self.config.moonraker_path.strip("/")
        path = f"/{normalized_path}" if normalized_path else ""
        return f"{proto}://{self.config.moonraker_host}:{self.config.moonraker_port}{path}/websocket"

    def get(
        self,
        endpoint: str,
        timeout: float = 4.0,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        self.policy.validate_http("GET", endpoint)
        headers = (
            {"x-api-key": self.config.moonraker_api_key} if self.config.moonraker_api_key else {}
        )
        response = requests.get(
            f"{self.endpoint}/{endpoint.strip('/')}",
            headers=headers,
            params=params,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        result = payload["result"] if isinstance(payload, dict) and "result" in payload else payload
        return cast(dict[str, Any], result)

    def get_server_info(self) -> dict[str, Any]:
        return self.get("server/info")

    def get_printer_info(self) -> dict[str, Any]:
        return self.get("printer/info")

    def get_objects_list(self) -> dict[str, Any]:
        return self.get("printer/objects/list")

    def get_printer_objects_query(self, objects: tuple[str, ...] = ()) -> dict[str, Any]:
        params = {name: _query_fields_for_object(name) for name in objects} if objects else None
        return self.get("printer/objects/query", params=params)

    def get_printer_objects_query_fields(self, fields_by_object: dict[str, str]) -> dict[str, Any]:
        return self.get("printer/objects/query", params=fields_by_object or None)

    def get_gcode_file_list(self) -> list[dict[str, Any]]:
        result = self.get("server/files/list", params={"root": "gcodes"})
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        return []

    def get_temperature_store(self) -> dict[str, Any]:
        return self.get("server/temperature_store")

    def get_machine_update_status(self) -> dict[str, Any]:
        return self.get("machine/update/status")


def _query_fields_for_object(name: str) -> str:
    if name == "print_stats":
        return "state,filename,print_duration,total_duration,filament_used,info"
    if name == "display_status":
        return "progress,message"
    if name == "virtual_sdcard":
        return "progress,is_active,file_path"
    if name == "toolhead":
        return "position,homed_axes,max_accel,max_velocity"
    if name == "gcode_move":
        return "gcode_position,homing_origin,speed,speed_factor,extrude_factor"
    return "temperature,target"
