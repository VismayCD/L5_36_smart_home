"""Smart home device controller.

Adds devices to rooms, switches them on and off, keeps the thermostat
within a safe range, lists devices by room, reports power use and saves
the home state to a JSON file.
"""

import json
import os
import shutil
import subprocess  # nosec B404 - only used with a fixed argument list below
from pathlib import Path

# Bind to localhost by default; exposing the hub on every interface must be
# an explicit choice made through the environment, not a hard-coded default.
HUB_HOST = os.environ.get("SMART_HOME_HUB_HOST", "127.0.0.1")
HUB_PORT = 8080
POWER_USAGE = {"light": 10, "fan": 60, "thermostat": 1500, "tv": 120}
# Secrets never live in source code: read the password from the environment.
HUB_PASSWORD = os.environ.get("SMART_HOME_HUB_PASSWORD", "")
SCENES_DIR = Path(__file__).resolve().parent / "scenes"
MIN_TEMPERATURE = 16
MAX_TEMPERATURE = 30

# Registry of every device, keyed by device name. The name is bound once
# (a module constant); only the dictionary's contents change at runtime.
DEVICES = {}


def add_device(device_name, kind, room="Living Room", settings=None):
    """Register a device in a room, switched off.

    ``settings`` defaults to None rather than ``{}``: a ``{}`` default is
    created once and shared by every call, so a temperature set on the
    thermostat would also appear on every other device added without
    explicit settings. A fresh dictionary is now made for each device.
    """
    DEVICES[device_name] = {"kind": kind, "room": room, "on": False,
                            "settings": dict(settings) if settings else {}}


def toggle_device(device_name):
    """Flip a device on/off and return its new state, or None if unknown."""
    device = DEVICES.get(device_name)
    if device is None:
        print("Device not found:", device_name)
        return None
    device["on"] = not device["on"]
    return device["on"]


def set_temperature(device_name, value):
    """Set a thermostat, clamped to the safe range; return True on success."""
    device = DEVICES.get(device_name)
    if device is None:
        print("Device not found:", device_name)
        return False
    if device["kind"] != "thermostat":
        print(device_name, "is not a thermostat")
        return False
    clamped = min(max(value, MIN_TEMPERATURE), MAX_TEMPERATURE)
    device["settings"]["temperature"] = clamped
    return True


def devices_in_room(room):
    """Return the names of all devices in the given room."""
    return [name for name, info in DEVICES.items() if info["room"] == room]


def power_usage():
    """Return the total power draw, in watts, of every device that is on."""
    active = [info for info in DEVICES.values() if info["on"]]
    return sum(POWER_USAGE.get(info["kind"], 0) for info in active)


def save_state(file_name="home_state.json"):
    """Write every device and its state to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as state_file:
        json.dump(DEVICES, state_file, indent=2)


def hub_address():
    """Return the hub's address as host:port."""
    return f"{HUB_HOST}:{HUB_PORT}"


def run_scene(scene_script):
    """Run a scene script from the scenes/ folder and return its exit code.

    Helper kept for the lab: not called by the demo.
    """
    script = (SCENES_DIR / scene_script).resolve()
    # Only plain files directly inside scenes/ may run: this blocks
    # "../../etc/x", absolute paths and "a.sh; rm -rf ~" style input.
    if script.parent != SCENES_DIR or not script.is_file():
        raise ValueError(f"Unknown scene script: {scene_script}")
    bash = shutil.which("bash")
    if bash is None:
        raise RuntimeError("bash is not available on this system")
    # A list of arguments with no shell: nothing in the name is interpreted.
    result = subprocess.run([bash, str(script)], check=False)  # nosec B603
    return result.returncode


def main():
    """Run a short demonstration of the controller."""
    add_device("Ceiling Light", "light")
    add_device("Bedroom Fan", "fan", "Bedroom")
    add_device("Thermostat", "thermostat", "Bedroom")
    add_device("Smart TV", "tv")
    toggle_device("Ceiling Light")
    toggle_device("Thermostat")
    toggle_device("Garage Door")
    set_temperature("Thermostat", 35)
    set_temperature("Ceiling Light", 20)
    print("Bedroom devices:", devices_in_room("Bedroom"))
    print("Current power use (W):", power_usage())
    print("Hub address:", hub_address())  # for app setup
    print("Light settings:", DEVICES["Ceiling Light"]["settings"])
    devices_on = [name for name, info in DEVICES.items() if info["on"]]
    print("Devices on:", devices_on)
    save_state()


if __name__ == "__main__":
    main()
