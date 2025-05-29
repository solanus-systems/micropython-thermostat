# micropython-thermostat

An advanced thermostat for micropython devices using `asyncio`.

## Installation

On a micropython device, install with `mip`:

```bash
mip install github:solanus-systems/micropython-thermostat
```

## Usage

```python
from thermostat import Thermostat

# Create a thermostat instance
therm = Thermostat()

# Heat to 65 degrees
therm.set_setpoint(65)
therm.set_mode_heat()

# Example sensor polling function; replace with your own
def read_sensor_temp():
  return 60

# After updating temp, check the heat relay flag
therm.set_temp(read_sensor_temp())
assert therm.heating.is_set()
```

See `thermostat.py` for the full API.

## Developing

You need python and a build of micropython with `asyncio` support. Follow the steps in the CI workflow to get a `micropython` binary and add it to your `PATH`.

Before making changes, install the development dependencies:

```bash
pip install -r dev-requirements.txt
```

After making changes, you can run the linter:

```bash
ruff check
```

Before running tests, install the test dependencies:

```bash
cat test-requirements.txt | grep -v "^$" | xargs -n 1 micropython -m mip install
```

Then, you can run the tests using the micropython version of `unittest`:

```bash
micropython -m unittest
```
