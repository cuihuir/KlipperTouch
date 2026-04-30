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
        if isinstance(payload, dict) and "error" in payload:
            raise RuntimeError(_jsonrpc_error_message(payload["error"]))
        result = payload["result"] if isinstance(payload, dict) and "result" in payload else payload
        return cast(dict[str, Any], result)

    def delete(self, endpoint: str, timeout: float = 4.0) -> dict[str, Any]:
        self.policy.validate_http("DELETE", endpoint)
        headers = (
            {"x-api-key": self.config.moonraker_api_key} if self.config.moonraker_api_key else {}
        )
        response = requests.delete(
            f"{self.endpoint}/{endpoint.strip('/')}",
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and "error" in payload:
            raise RuntimeError(_jsonrpc_error_message(payload["error"]))
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

    def post_jsonrpc(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        timeout: float = 4.0,
    ) -> dict[str, Any]:
        self.policy.validate_jsonrpc(method)
        headers = (
            {"x-api-key": self.config.moonraker_api_key} if self.config.moonraker_api_key else {}
        )
        response = requests.post(
            f"{self.endpoint}/server/jsonrpc",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "method": method,
                "params": params or {},
                "id": 1,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and "error" in payload:
            raise RuntimeError(_jsonrpc_error_message(payload["error"]))
        result = payload["result"] if isinstance(payload, dict) and "result" in payload else payload
        return cast(dict[str, Any], result)

    def get_printer_objects_query_jsonrpc(
        self,
        objects: dict[str, list[str]],
    ) -> dict[str, Any]:
        return self.post_jsonrpc(
            "printer.objects.query",
            params={"objects": objects},
        )

    def start_print(self, filename: str) -> dict[str, Any]:
        return self.post_jsonrpc("printer.print.start", params={"filename": filename})

    def pause_print(self) -> dict[str, Any]:
        return self.post_jsonrpc("printer.print.pause")

    def resume_print(self) -> dict[str, Any]:
        return self.post_jsonrpc("printer.print.resume")

    def cancel_print(self) -> dict[str, Any]:
        return self.post_jsonrpc("printer.print.cancel")

    def firmware_restart(self) -> dict[str, Any]:
        return self.post_jsonrpc("printer.firmware_restart")

    def restart_klipper(self) -> dict[str, Any]:
        return self.post_jsonrpc("printer.restart")

    def emergency_stop(self) -> dict[str, Any]:
        return self.post_jsonrpc("printer.emergency_stop")

    def run_gcode_script(self, script: str) -> dict[str, Any]:
        return self.post_jsonrpc("printer.gcode.script", params={"script": script})

    def adjust_z_offset(self, delta: float) -> dict[str, Any]:
        return self.run_gcode_script(f"SET_GCODE_OFFSET Z_ADJUST={delta:.3f} MOVE=1")

    def set_speed_factor(self, percent: float) -> dict[str, Any]:
        return self.run_gcode_script(f"M220 S{percent:.0f}")

    def set_extrude_factor(self, percent: float) -> dict[str, Any]:
        return self.run_gcode_script(f"M221 S{percent:.0f}")

    def exclude_object(self, object_name: str) -> dict[str, Any]:
        return self.run_gcode_script(f"EXCLUDE_OBJECT NAME={object_name}")

    def clear_sdcard_file(self) -> dict[str, Any]:
        return self.run_gcode_script("SDCARD_RESET_FILE")

    def disable_motors(self) -> dict[str, Any]:
        return self.run_gcode_script("M84")

    def jog_toolhead(self, axis: str, distance: float, speed: float) -> dict[str, Any]:
        normalized_axis = axis.lower()
        if normalized_axis not in {"x", "y", "z", "u", "v", "w"}:
            raise ValueError("Invalid jog axis")
        if speed <= 0:
            raise ValueError("Invalid jog speed")
        feedrate = float(speed) * 60
        script = f"_CLIENT_LINEAR_MOVE {normalized_axis.upper()}={distance:.3f} F={feedrate:.0f}"
        return self.run_gcode_script(script)

    def home_axes(self, *axes: str) -> dict[str, Any]:
        normalized_axes = tuple(axis.lower() for axis in axes)
        if any(axis not in {"x", "y", "z", "u", "v", "w"} for axis in normalized_axes):
            raise ValueError("Invalid home axis")
        suffix = " ".join(axis.upper() for axis in normalized_axes)
        script = f"G28 {suffix}".strip()
        return self.run_gcode_script(script)

    def run_z_tilt_adjust(self) -> dict[str, Any]:
        return self.run_gcode_script("Z_TILT_ADJUST")

    def run_accelerator_level(self) -> dict[str, Any]:
        return self.run_gcode_script("ACCELERATOR_LEVEL MOVE=1")

    def run_uvw_home(self) -> dict[str, Any]:
        return self.run_gcode_script("UVW_HOME")

    def extrude_filament(self, distance: float, speed: float) -> dict[str, Any]:
        return self.run_gcode_script(f"_CLIENT_LINEAR_MOVE E={distance:.3f} F={speed * 60:.0f}")

    def load_filament(self, speed: float) -> dict[str, Any]:
        return self.run_gcode_script(f"LOAD_FILAMENT SPEED={speed * 60:.0f}")

    def unload_filament(self, speed: float) -> dict[str, Any]:
        return self.run_gcode_script(f"UNLOAD_FILAMENT SPEED={speed * 60:.0f}")

    def set_temperature_target(self, device_name: str, target: float) -> dict[str, Any]:
        clean_name = device_name.strip()
        if clean_name.startswith("temperature_fan "):
            fan_name = clean_name.removeprefix("temperature_fan ").strip()
            return self.run_gcode_script(
                f'SET_TEMPERATURE_FAN_TARGET temperature_fan="{fan_name}" target={target:.0f}'
            )
        return self.run_gcode_script(
            f'SET_HEATER_TEMPERATURE heater="{clean_name}" target={target:.0f}'
        )

    def set_pressure_advance(self, advance: float, smooth_time: float) -> dict[str, Any]:
        return self.run_gcode_script(
            f"SET_PRESSURE_ADVANCE ADVANCE={advance:.3f} SMOOTH_TIME={smooth_time:.3f}"
        )

    def set_fan_speed(self, device_name: str, percent: float) -> dict[str, Any]:
        clean_name = device_name.strip()
        if percent < 0 or percent > 100:
            raise ValueError("Fan speed must be between 0 and 100")
        if clean_name == "fan":
            pwm = round(float(percent) * 255 / 100)
            return self.run_gcode_script(f"M106 S{pwm:.0f}")
        if clean_name.startswith("fan_generic "):
            fan_name = clean_name.removeprefix("fan_generic ").strip()
            return self.run_gcode_script(
                f'SET_FAN_SPEED FAN="{fan_name}" SPEED={float(percent) / 100:.3f}'
            )
        raise ValueError("Fan is not controllable")

    def delete_gcode_file(self, filename: str) -> dict[str, Any]:
        return self.delete(f"server/files/gcodes/{filename.strip('/')}")

    def upload_gcode_file(
        self,
        filename: str,
        content: bytes,
        *,
        path: str = "",
        print_after_upload: bool = False,
        timeout: float = 8.0,
    ) -> dict[str, Any]:
        self.policy.validate_http("POST", "server/files/upload")
        headers = (
            {"x-api-key": self.config.moonraker_api_key} if self.config.moonraker_api_key else {}
        )
        response = requests.post(
            f"{self.endpoint}/server/files/upload",
            headers=headers,
            data={
                "root": "gcodes",
                "path": path.strip("/"),
                "print": "true" if print_after_upload else "false",
            },
            files={"file": (filename.strip("/"), content, "text/plain")},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and "error" in payload:
            raise RuntimeError(_jsonrpc_error_message(payload["error"]))
        result = payload["result"] if isinstance(payload, dict) and "result" in payload else payload
        return cast(dict[str, Any], result)

    def get_gcode_file_list(self) -> list[dict[str, Any]]:
        result = self.get("server/files/list", params={"root": "gcodes"})
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        return []

    def get_gcode_file_metadata(self, filename: str) -> dict[str, Any]:
        return self.get("server/files/metadata", params={"filename": filename})

    def get_temperature_store(self) -> dict[str, Any]:
        return self.get("server/temperature_store")

    def get_machine_update_status(self) -> dict[str, Any]:
        return self.get("machine/update/status")


def _query_fields_for_object(name: str) -> str:
    if name == "extruder":
        return "temperature,target,can_extrude,pressure_advance,smooth_time"
    if name.startswith(("filament_switch_sensor ", "filament_motion_sensor ")):
        return "enabled,filament_detected"
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
    if name == "webhooks":
        return "state,state_message"
    if name == "configfile":
        return "config,settings,warnings"
    return "temperature,target"


def _jsonrpc_error_message(error: Any) -> str:
    if isinstance(error, dict):
        message = error.get("message")
        if message:
            return str(message)
    return str(error)
