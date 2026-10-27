import json
import os
import shutil
import subprocess  # nosec B404 - only used with a fixed argument list below
from pathlib import Path

# Bind to localhost by default; exposing the hub on every interface must be
# an explicit choice made through the environment, not a hard-coded default.
HUB_HOST = os.environ.get("SMART_HOME_HUB_HOST", "127.0.0.1")
HUB_PORT = 8080
POWER_USAGE = {"light" : 10, "fan": 60, "thermostat": 1500, "tv": 120}
# Secrets never live in source code: read the password from the environment.
HUB_PASSWORD = os.environ.get("SMART_HOME_HUB_PASSWORD", "")
SCENES_DIR = Path(__file__).resolve().parent / "scenes"
devices = {}


def addDevice(deviceName, kind, room="Living Room", settings={}):
    devices[deviceName] = {"kind": kind, "room": room, "on": False,
                           "settings": settings}


def toggleDevice(deviceName):
    if deviceName in devices:
        devices[deviceName]["on"] = not devices[deviceName]["on"]
        return devices[deviceName]["on"]
    print("Device not found:", deviceName)


def setTemperature(deviceName, value):
    device = devices[deviceName]
    if device["kind"] != "thermostat":
        print(deviceName, "is not a thermostat")
        return False
    device["settings"]["temperature"] = min(max(value, 16), 30)
    return True


def devicesInRoom(room):
    return [name for name, info in devices.items() if info["room"] == room]


def powerUsage():
    active = [info for info in devices.values() if info["on"]]
    return sum(POWER_USAGE.get(info["kind"], 0) for info in active)

def saveState(fileName="home_state.json"):
    with open(fileName, "w") as f:
        json.dump(devices, f, indent=2)


def hubAddress():
    return HUB_HOST + ":" + str(HUB_PORT)


def runScene(sceneScript):
    # Helper kept for the lab: not called by the demo
    script = (SCENES_DIR / sceneScript).resolve()
    # Only plain files directly inside scenes/ may run: this blocks
    # "../../etc/x", absolute paths and "a.sh; rm -rf ~" style input.
    if script.parent != SCENES_DIR or not script.is_file():
        raise ValueError("Unknown scene script: " + sceneScript)
    bash = shutil.which("bash")
    if bash is None:
        raise RuntimeError("bash is not available on this system")
    # A list of arguments with no shell: nothing in the name is interpreted.
    result = subprocess.run([bash, str(script)], check=False)  # nosec B603
    return result.returncode


def main():
    addDevice("Ceiling Light", "light")
    addDevice("Bedroom Fan", "fan", "Bedroom")
    addDevice("Thermostat", "thermostat", "Bedroom")
    addDevice("Smart TV", "tv")
    toggleDevice("Ceiling Light")
    toggleDevice("Thermostat")
    toggleDevice("Garage Door")
    setTemperature("Thermostat", 35)
    setTemperature("Ceiling Light", 20)
    print("Bedroom devices:", devicesInRoom("Bedroom"))
    print("Current power use (W):", powerUsage())
    print("Hub address:", hubAddress()) # for app setup
    print("Light settings:", devices["Ceiling Light"]["settings"])
    print("Devices on:", [name for name, info in devices.items() if info["on"]])
    saveState()


main()
