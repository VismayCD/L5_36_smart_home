# Lab 5: Reflection

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the Flake8 style issues (E203, E302, E261, E501) and the missing docstrings. Each message names the exact line and column and the fix is mechanical: remove a space, add a blank line, split a long line. They cannot change how the program behaves.

**Hardest:** the shell-injection issue (Bandit B602) in `runScene`. Removing `shell=True` alone was not enough. I also had to decide what input is allowed: only a plain file inside `scenes/`, which rules out `../` paths, absolute paths and names containing `;`. I had to call `bash` by its full path with a list of arguments, and then judge whether the leftover low-severity warnings (B404/B603) were real risks or just "please review" notes. The mutable default argument was also tricky because the program *looked* like it worked. It only showed up as `Light settings: {'temperature': 30}`, a light with a temperature, and understanding why needs knowing that Python evaluates default values once, when the function is defined.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes. After the injection fix, Bandit still reports **B404** (`import subprocess`) and **B603** (`subprocess` call without `shell=True`). These are not vulnerabilities: the call uses a fixed argument list and no shell, and the script name has already been checked. Bandit flags every use of `subprocess` so that a human reviews it. I reviewed them and marked them with targeted `# nosec B404` / `# nosec B603` comments that explain why. Targeted comments do not hide unrelated future findings on those lines the way a bare `# nosec` would.

**B105** (hard-coded password) is borderline. `"smarthome-demo"` is a demo value, but Bandit is right that a password literal in source code is a bad habit, so I moved it to an environment variable. Some Pylint naming messages are also matters of convention more than errors. Renaming `devices` to `DEVICES` treats the registry as a module-level constant, which is true of the name even though the dictionary's contents change.

### 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint in the editor (VS Code / PyCharm extensions) so issues show up while typing. Add a **pre-commit** hook (`.pre-commit-config.yaml` with flake8, pylint and bandit) so a commit with new issues is blocked before it reaches the repository.
- **In CI:** add a GitHub Actions job that runs `flake8`, `pylint --fail-under=9.5` and `bandit -r . -ll` (medium and above) on every push and pull request, and require it to pass before merging. Upload the reports as build artifacts so reviewers can read them.
- **Configuration:** keep shared settings in `pyproject.toml` / `.flake8` / `.bandit` so everyone runs the same rules. Disable checks only with justified, targeted comments, never by turning a rule off for the whole project.
- **Legacy code:** start from a baseline (`bandit -b baseline.json`) so only *new* issues fail the build, then reduce old ones gradually.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Correctness:** the shared-dictionary bug is gone. Only the thermostat has a temperature, and each device's settings are independent. `set_temperature` no longer crashes with `KeyError` on an unknown device, and `toggle_device` always returns a defined value.
- **Security:** `run_scene` can no longer be used to run arbitrary shell commands, no password is stored in the code, and the hub listens only on localhost unless configured otherwise.
- **Readability:** consistent snake_case names, docstrings on every function, named constants (`MIN_TEMPERATURE`, `MAX_TEMPERATURE`) instead of magic numbers, and PEP 8 formatting make the file quicker to read and review.
- **Maintainability:** the `__main__` guard lets the module be imported and tested without running the demo. An explicit UTF-8 encoding makes the saved JSON identical on every OS. All three tools now pass cleanly, so any new warning in future stands out right away.
- **Measured:** Flake8 went from 4 issues to 0. Pylint and Bandit before/after figures are in `reports/`.
