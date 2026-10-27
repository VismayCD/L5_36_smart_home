# Lab 5: Static Code Analysis — Issue Documentation

**File:** `smart_home.py` · **Tools:** Pylint, Bandit, Flake8

Line numbers refer to the **original** `smart_home.py` (commit `Initial commit`).
High- and medium-severity issues are listed first.

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 1 | Shell command injection (Bandit **B602**, severity **High**) | Security | 51 | `runScene` built a command by string concatenation (`"bash scenes/" + sceneScript`) and ran it with `shell=True`. A name such as `x.sh; rm -rf ~` would run a second command. | Resolve the script path and allow only a plain file directly inside `scenes/`. Find `bash` with `shutil.which` and call `subprocess.run([bash, script], check=False)` with an argument list and no shell. |
| 2 | Mutable default argument (Pylint **W0102** `dangerous-default-value`) | Bug | 11–13 | `settings={}` is created once and shared by every device added without settings. Setting the thermostat to 30 °C made the demo print `Light settings: {'temperature': 30}`. | Default changed to `settings=None`, and a new dict is created for each device (`dict(settings) if settings else {}`). The demo now prints `Light settings: {}`. |
| 3 | Binding to all interfaces (Bandit **B104**, severity **Medium**) | Security | 4 | `HUB_HOST = "0.0.0.0"` exposes the hub on every network interface. It is also not an address an app can connect to, so "Hub address: 0.0.0.0:8080" was misleading. | Default to `127.0.0.1`. Allow an explicit override through the `SMART_HOME_HUB_HOST` environment variable. |
| 4 | Hard-coded password (Bandit **B105**, severity Low, confidence Medium) | Security | 7 | `HUB_PASSWORD = "smarthome-demo"` puts a secret in source code and git history. | Read it from the `SMART_HOME_HUB_PASSWORD` environment variable instead. |
| 5 | Inconsistent return statements (Pylint **R1710**) | Bug / Design | 16–20 | `toggleDevice` returned a bool on success but fell off the end (implicit `None`) when the device was missing. | Look up the device with `.get()` and `return None` explicitly when it is not found. |
| 6 | Crash on unknown device (found by reading the code; no tool flags it) | Bug | 24 | `setTemperature` indexed `devices[deviceName]` directly, so an unknown name raised `KeyError`. | Use `DEVICES.get()`, print "Device not found" and return `False`, consistent with `toggle_device`. |
| 7 | File opened without encoding (Pylint **W1514** `unspecified-encoding`) | Bug (portability) | 41 | `open(fileName, "w")` uses the platform default encoding, so the JSON differs between Windows and Linux. | `open(file_name, "w", encoding="utf-8")`. |
| 8 | Subprocess import / call (Bandit **B404**, **B603**, severity Low) | Security (review) | 2, 51 | Bandit flags every use of `subprocess` for manual review. | Reviewed after fix #1: the call uses a fixed argument list and no shell. Marked with targeted `# nosec B404` / `# nosec B603` comments that give a reason. |
| 9 | Naming convention (Pylint **C0103** `invalid-name`) | Style | 8, 11, 16, 23, 32, 36, 40, 45, 49 | camelCase functions and arguments (`addDevice`, `deviceName`, `fileName`, …) and a lowercase module-level name (`devices`). | Renamed to snake_case (`add_device`, `device_name`, …). The registry is now `DEVICES`. |
| 10 | Missing docstrings (Pylint **C0114**, **C0116**) | Style / Docs | 1, 11–54 | No module docstring and no function docstrings. | Added a module docstring and one docstring per function. |
| 11 | Code runs on import (found by reading the code; no tool flags it) | Design | 72 | `main()` was called at module level, so importing the file, for example in a test, ran the demo and wrote `home_state.json`. | Wrapped it in `if __name__ == "__main__": main()`. |
| 12 | Whitespace before `:` (Flake8 **E203**) | Style | 6 | `{"light" : 10, …}` | Removed the space: `{"light": 10, …}`. |
| 13 | Expected 2 blank lines (Flake8 **E302**) | Style | 40 | Only one blank line before `def saveState`. | Added the second blank line. |
| 14 | Inline comment spacing (Flake8 **E261**) | Style | 66 | One space before `# for app setup`. | Two spaces before the inline comment. |
| 15 | Line too long (Flake8 **E501**) | Style | 68 | 80 characters (limit 79). | Moved the list comprehension into a `devices_on` variable before printing. |

Also improved: the magic numbers `16` and `30` became `MIN_TEMPERATURE` / `MAX_TEMPERATURE`, and `hub_address` uses an f-string.

## Commits

| Commit | Tool | Issues fixed |
|--------|------|--------------|
| `Fix security issues reported by Bandit` | Bandit | 1, 3, 4, 8 |
| `Fix code quality issues reported by Pylint` | Pylint | 2, 5, 6, 7, 9, 10, 11 |
| `Fix PEP 8 style issues reported by Flake8` | Flake8 | 12, 13, 14, 15 |
