import logging
from asyncio import Event
from collections import namedtuple
from time import localtime, mktime

# Structure to hold temperature readings
TemperatureReading = namedtuple("TemperatureReading", ["value", "timestamp"])


class Thermostat:
    """A Thermostat with temperature memory, single/dual setpoints, etc."""

    SETPOINT_MAX = 100
    SETPOINT_MIN = 0

    CALIBRATION_MAX = 5
    CALIBRATION_MIN = -5

    DIFFERENTIAL_MAX = 5
    DIFFERENTIAL_MIN = 0

    MODE_SINGLE = "single"
    MODE_DUAL = "dual"
    MODE_HEAT = "heat"
    MODE_COOL = "cool"

    STATE_OFF = "off"
    STATE_ON = "on"

    DEFAULT_WINDOW_LEN = 1 * 60 * 60  # 1 hour in seconds
    DEFAULT_QUEUE_LEN = 10  # Temperature readings to keep

    def __init__(
        self,
        queue_len: int = DEFAULT_QUEUE_LEN,
        window_len: int = DEFAULT_WINDOW_LEN,
        logger: logging.Logger | None = None,
    ):
        if queue_len <= 0:
            raise ValueError("Temperature queue_len must be a positive integer")
        if window_len <= 0:
            raise ValueError("Temperature window_len must be a positive integer")
        self.logger = logger or logging.getLogger("thermostat")

        # Initial state
        self._setpoint = None
        self._cool_setpoint = None
        self._heat_setpoint = None
        self._differential = 1
        self._calibration = 0
        # self._temps: deque[TemperatureReading] = deque([], queue_len)
        self._temps: list[TemperatureReading] = []
        self._queue_len = queue_len
        self._window_len = window_len

        # Event flags for heating and cooling
        self.heating = Event()
        self.cooling = Event()

        # Turn it on
        self.set_mode_single()
        self.set_state_online()

    @property
    def setpoint(self):
        """Get the current setpoint for heat+cool or 'hold' mode."""
        return self._setpoint

    @property
    def cool_setpoint(self):
        """Get the current cooling setpoint."""
        return self._cool_setpoint

    @property
    def heat_setpoint(self):
        """Get the current heating setpoint."""
        return self._heat_setpoint

    @property
    def calibration(self):
        """Get the current calibration offset for the temperature sensor."""
        return self._calibration

    @property
    def differential(self):
        """Get the current differential or 'tolerance' value."""
        return self._differential

    @property
    def current_temp(self):
        """Get the current (most recently recorded) temperature."""
        return self._temps[-1].value if len(self._temps) > 0 else None

    @property
    def mode(self):
        """Get the current mode of the thermostat."""
        return self._mode

    @property
    def online(self):
        """Check if the thermostat is online."""
        return self._state == self.STATE_ON

    @property
    def avg_temp_change(self):
        """Calculate the average temperature change from recent measurements."""
        # Ensure we have enough data to start with
        if len(self._temps) < 2:
            return 0.0

        # Discard temperatures outside the window; ensure we still have enough data
        recent_temps = self.temp_history(full=False)
        if len(recent_temps) < 2:
            return 0.0

        # Average the changes between consecutive readings
        total_change = sum(
            recent_temps[i].value - recent_temps[i - 1].value
            for i in range(1, len(recent_temps))
        )
        return total_change / (len(recent_temps) - 1)

    def set_state_online(self):
        """Turn the thermostat on."""
        self._state = self.STATE_ON
        self.logger.info("Thermostat online")

    def set_state_offline(self):
        """Turn the thermostat off and reset relays."""
        self._state = self.STATE_OFF
        self.logger.info("Thermostat offline")
        self.heating.clear()
        self.cooling.clear()

    def temp_history(self, full=True):
        """Get the temperature history (optionally, within the window only)."""
        if full:
            return self._temps

        start_of_window = mktime(localtime()) - self._window_len
        return [t for t in self._temps if t.timestamp >= start_of_window]

    def set_mode_single(self):
        """Set the thermostat to single mode (heat+cool or 'hold')."""
        self._mode = self.MODE_SINGLE
        self.heating.clear()
        self.cooling.clear()
        self.logger.info("Thermostat mode set to single")

    def set_mode_dual(self):
        """Set the thermostat to dual mode (separate heat and cool setpoints)."""
        self._mode = self.MODE_DUAL
        self.heating.clear()
        self.cooling.clear()
        self.logger.info("Thermostat mode set to dual")

    def set_mode_heat(self):
        """Set the thermostat to heating mode only."""
        self._mode = self.MODE_HEAT
        self.heating.clear()
        self.cooling.clear()
        self.logger.info("Thermostat mode set to heat")

    def set_mode_cool(self):
        """Set the thermostat to cooling mode only."""
        self._mode = self.MODE_COOL
        self.heating.clear()
        self.cooling.clear()
        self.logger.info("Thermostat mode set to cool")

    def set_setpoint(self, value: int):
        """Set a single setpoint for heat+cool or 'hold' mode."""
        self._setpoint = self._validate_setpoint(value)
        self.logger.info(f"Setpoint set to {self._setpoint}°")
        return self._setpoint

    def set_cool_setpoint(self, value: int):
        """Set the cooling setpoint."""
        cool_setpoint = self._validate_setpoint(value)
        if self.heat_setpoint and (
            cool_setpoint < self.heat_setpoint + self.differential
        ):
            raise ValueError(
                f"Cool setpoint {cool_setpoint}° invalid relative to heat setpoint ({self.heat_setpoint}°)"
            )
        self._cool_setpoint = cool_setpoint
        self.logger.info(f"Cool setpoint set to {self._cool_setpoint}°")
        return self._cool_setpoint

    def set_heat_setpoint(self, value: int):
        """Set the heating setpoint."""
        heat_setpoint = self._validate_setpoint(value)
        if self.cool_setpoint and (
            heat_setpoint > self.cool_setpoint - self.differential
        ):
            raise ValueError(
                f"Heat setpoint {heat_setpoint}° invalid relative to cool setpoint ({self.cool_setpoint}°)"
            )
        self._heat_setpoint = heat_setpoint
        self.logger.info(f"Heat setpoint set to {self._heat_setpoint}°")
        return self._heat_setpoint

    def set_calibration(self, value: int):
        """Set the calibration offset for the temperature sensor."""
        if value < self.CALIBRATION_MIN or value > self.CALIBRATION_MAX:
            raise ValueError(
                f"Calibration {value}° is out of range ({self.CALIBRATION_MIN}° to {self.CALIBRATION_MAX}°)"
            )
        self._calibration = value
        self.logger.info(f"Calibration set to {self._calibration}°")
        return self._calibration

    def set_differential(self, value: int):
        """Set the differential or 'tolerance' value before relays are activated."""
        if value < self.DIFFERENTIAL_MIN or value > self.DIFFERENTIAL_MAX:
            raise ValueError(
                f"Differential {value}° is out of range ({self.DIFFERENTIAL_MIN}° to {self.DIFFERENTIAL_MAX}°)"
            )
        self._differential = value
        self.logger.info(f"Differential set to {self._differential}°")
        return self._differential

    def set_temp(self, value: float):
        """Update the current temperature, apply calibration, and update state."""
        if not self.online:
            raise RuntimeError("Cannot set temperature while thermostat is offline")

        # Read and calibrate the temperature
        self.logger.debug(f"Received temperature: {value}°")
        calibrated_temp = value + self.calibration
        if self.calibration != 0:
            self.logger.debug(f"Calibrated temperature to {calibrated_temp}°")

        # Remove last temperature if the queue is full
        self._temps.append(
            TemperatureReading(value=calibrated_temp, timestamp=mktime(localtime()))
        )
        if len(self._temps) > self._queue_len:
            del self._temps[0]

        self._update_relays()

        # TODO: high and low temp alerts
        # TODO: inverse logic detection, fault detection, etc.

    def _should_heat(self):
        """Check if heating should be activated based on the mode and current temperature."""
        if not self.current_temp or self.mode == self.MODE_COOL:
            return False

        if self.mode == self.MODE_SINGLE:
            return (
                self.setpoint is not None
                and self.current_temp < self.setpoint - self.differential
            )

        if self.mode == self.MODE_DUAL or self.mode == self.MODE_HEAT:
            return (
                self.heat_setpoint is not None
                and self.current_temp < self.heat_setpoint - self.differential
            )

        return False

    def _should_cool(self):
        """Check if cooling should be activated based on the mode and current temperature."""
        if not self.current_temp or self.mode == self.MODE_HEAT:
            return False

        if self.mode == self.MODE_SINGLE:
            return (
                self.setpoint is not None
                and self.current_temp > self.setpoint + self.differential
            )

        if self.mode == self.MODE_DUAL or self.mode == self.MODE_COOL:
            return (
                self.cool_setpoint is not None
                and self.current_temp > self.cool_setpoint + self.differential
            )

        return False

    def _update_relays(self):
        """Update the thermostat relays based on the current temperature."""
        # Heating logic
        if self._should_heat() and not self.heating.is_set():
            self.logger.info("Heating ON")
            self.heating.set()
        if not self._should_heat() and self.heating.is_set():
            self.logger.info("Heating OFF")
            self.heating.clear()

        # Cooling logic
        if self._should_cool() and not self.cooling.is_set():
            self.logger.info("Cooling ON")
            self.cooling.set()
        if not self._should_cool() and self.cooling.is_set():
            self.logger.info("Cooling OFF")
            self.cooling.clear()

    def _validate_setpoint(self, value):
        """Validate that the setpoint is within the allowed range."""
        if value < self.SETPOINT_MIN:
            raise ValueError(
                f"Setpoint {value}° is below minimum ({self.SETPOINT_MIN}°)"
            )
        if value > self.SETPOINT_MAX:
            raise ValueError(
                f"Setpoint {value}° is above maximum ({self.SETPOINT_MAX}°)"
            )
        return value
