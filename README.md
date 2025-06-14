# micropython-thermostat

[![ci](https://github.com/solanus-systems/micropython-thermostat/actions/workflows/ci.yml/badge.svg)](https://github.com/solanus-systems/micropython-thermostat/actions/workflows/ci.yml)

An advanced thermostat for micropython devices using `asyncio`.

## Installation

On a micropython device, install with `mip` from the REPL:

```python
>>> import mip
>>> mip.install("github:solanus-systems/micropython-thermostat")
```

Or on a unix build of micropython via the CLI:

```bash
micropython -m mip install github:solanus-systems/micropython-thermostat
```

## Usage

This module implements async thermostat logic but does not include any hardware-specific code.

Setup generally involves:

1. Initialize a `Thermostat` instance and set the mode and setpoint(s)
1. Write a polling loop or other function to read temperature from a sensor
1. Call `set_temp()` to update with the temperature read from the sensor
1. Check or `await` the `heating` and `cooling` flags (`asyncio.Event` objects)
1. Use the flags to control relays or other hardware as needed

### Example

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

See `thermostat/__init__.py` for the full API.

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
./bin/setup
```

Then, you can run the tests using the micropython version of `unittest`:

```bash
micropython -m unittest
```

## Releasing

To release a new version, update the version in `package.json`. Commit your changes and make a pull request. After merging, create a new tag and push to GitHub:

```bash
git tag vX.Y.Z
git push --tags
```
