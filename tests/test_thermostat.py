from time import localtime, mktime
from unittest import TestCase

from src.lib.thermostat import TemperatureReading, Thermostat


class TestThermostat(TestCase):
    def test_validate_setpoint_single_max(self):
        """Single setpoint should not exceed max value"""
        thermostat = Thermostat()
        with self.assertRaises(ValueError):
            thermostat.set_setpoint(101)

    def test_validate_setpoint_single_min(self):
        """Single setpoint should not be below min value"""
        thermostat = Thermostat()
        with self.assertRaises(ValueError):
            thermostat.set_setpoint(-1)

    def test_validate_setpoint_single_valid(self):
        """Single setpoint should be valid within range"""
        thermostat = Thermostat()
        thermostat.set_setpoint(20)
        self.assertEqual(thermostat.setpoint, 20)

    def test_validate_setpoint_cool_max(self):
        """Cool setpoint should not exceed max value"""
        thermostat = Thermostat()
        with self.assertRaises(ValueError):
            thermostat.set_cool_setpoint(101)

    def test_validate_setpoint_cool_min(self):
        """Cool setpoint should not be below min value"""
        thermostat = Thermostat()
        with self.assertRaises(ValueError):
            thermostat.set_cool_setpoint(-1)

    def test_validate_setpoint_heat_max(self):
        """Heat setpoint should not exceed max value"""
        thermostat = Thermostat()
        with self.assertRaises(ValueError):
            thermostat.set_heat_setpoint(101)

    def test_validate_setpoint_heat_min(self):
        """Heat setpoint should not be below min value"""
        thermostat = Thermostat()
        with self.assertRaises(ValueError):
            thermostat.set_heat_setpoint(-1)

    def test_validate_setpoint_cool_relative_to_heat(self):
        """Cool setpoint must be greater than heat setpoint + differential"""
        thermostat = Thermostat()
        thermostat.set_differential(2)
        thermostat.set_heat_setpoint(20)
        with self.assertRaises(ValueError):
            thermostat.set_cool_setpoint(21)

    def test_validate_setpoint_heat_relative_to_cool(self):
        """Heat setpoint must be less than cool setpoint - differential"""
        thermostat = Thermostat()
        thermostat.set_differential(2)
        thermostat.set_cool_setpoint(25)
        with self.assertRaises(ValueError):
            thermostat.set_heat_setpoint(24)

    def test_validate_setpoint_dual_valid(self):
        """Cool and heat setpoints should be valid within range"""
        thermostat = Thermostat()
        thermostat.set_cool_setpoint(25)
        thermostat.set_heat_setpoint(20)
        self.assertEqual(thermostat.cool_setpoint, 25)
        self.assertEqual(thermostat.heat_setpoint, 20)

    def test_validate_calibration_max(self):
        """Calibration should not exceed max value"""
        thermostat = Thermostat()
        with self.assertRaises(ValueError):
            thermostat.set_calibration(6)

    def test_validate_calibration_min(self):
        """Calibration should not be below min value"""
        thermostat = Thermostat()
        with self.assertRaises(ValueError):
            thermostat.set_calibration(-6)

    def test_validate_calibration_valid(self):
        """Calibration should be valid within range"""
        thermostat = Thermostat()
        thermostat.set_calibration(3)
        self.assertEqual(thermostat.calibration, 3)

    def test_set_temp(self):
        """Temperature should be set correctly"""
        thermostat = Thermostat()
        thermostat.set_temp(20)
        self.assertEqual(thermostat.current_temp, 20)

    def test_calibration_applied(self):
        """Calibration should be applied to temperature"""
        thermostat = Thermostat()
        thermostat.set_calibration(2)
        thermostat.set_temp(20)
        self.assertEqual(thermostat.current_temp, 22)

    def test_single_setpoint_heat_activated(self):
        """Single setpoint should activate heating when below setpoint"""
        thermostat = Thermostat()
        thermostat.set_mode_single()
        thermostat.set_setpoint(20)
        thermostat.set_temp(18)
        self.assertTrue(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

    def test_single_setpoint_cool_activated(self):
        """Single setpoint should activate cooling when above setpoint"""
        thermostat = Thermostat()
        thermostat.set_mode_single()
        thermostat.set_setpoint(20)
        thermostat.set_temp(22)
        self.assertTrue(thermostat.cooling.is_set())
        self.assertFalse(thermostat.heating.is_set())

    def test_dual_setpoint_heat_activated(self):
        """Dual setpoint should activate heating when below heat setpoint"""
        thermostat = Thermostat()
        thermostat.set_mode_dual()
        thermostat.set_heat_setpoint(20)
        thermostat.set_temp(18)
        self.assertTrue(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

    def test_dual_setpoint_cool_activated(self):
        """Dual setpoint should activate cooling when above cool setpoint"""
        thermostat = Thermostat()
        thermostat.set_mode_dual()
        thermostat.set_cool_setpoint(25)
        thermostat.set_temp(27)
        self.assertTrue(thermostat.cooling.is_set())
        self.assertFalse(thermostat.heating.is_set())

    def test_single_setpoint_idle_differential(self):
        """Single setpoint should not activate heating or cooling within differential"""
        thermostat = Thermostat()
        thermostat.set_mode_single()
        thermostat.set_setpoint(20)
        thermostat.set_differential(2)
        thermostat.set_temp(19)
        self.assertFalse(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

        thermostat.set_temp(21)
        self.assertFalse(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

    def test_dual_setpoint_idle_differential(self):
        """Dual setpoint should not activate heating or cooling within differential"""
        thermostat = Thermostat()
        thermostat.set_mode_dual()
        thermostat.set_heat_setpoint(20)
        thermostat.set_cool_setpoint(25)
        thermostat.set_differential(2)

        thermostat.set_temp(19)
        self.assertFalse(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

        thermostat.set_temp(26)
        self.assertFalse(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

    def test_mode_switching(self):
        """Test switching between single and dual modes"""
        thermostat = Thermostat()

        # Start in single mode
        thermostat.set_mode_single()
        thermostat.set_setpoint(20)
        thermostat.set_temp(18)
        self.assertTrue(thermostat.heating.is_set())

        # Switch to dual mode
        thermostat.set_mode_dual()
        thermostat.set_heat_setpoint(20)
        thermostat.set_cool_setpoint(25)

        # Check heating and cooling states
        thermostat.set_temp(18)
        self.assertTrue(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

        thermostat.set_temp(28)
        self.assertFalse(thermostat.heating.is_set())
        self.assertTrue(thermostat.cooling.is_set())

    def test_mode_switch_clears_relays(self):
        """Test that switching modes clears heating and cooling relays"""
        thermostat = Thermostat()

        # Start in single mode
        thermostat.set_mode_single()
        thermostat.set_setpoint(20)
        thermostat.set_temp(18)
        self.assertTrue(thermostat.heating.is_set())

        # Switch to dual mode
        thermostat.set_mode_dual()
        self.assertFalse(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

    def test_state_on(self):
        """Test setting thermostat state to ON"""
        thermostat = Thermostat()
        thermostat.set_state_offline()
        thermostat.set_state_online()
        self.assertTrue(thermostat.online)

    def test_state_off(self):
        """Test setting thermostat state to OFF"""
        thermostat = Thermostat()
        thermostat.set_state_offline()
        self.assertFalse(thermostat.online)

    def test_state_off_clears_relays(self):
        """Test that setting state to OFF clears heating and cooling relays"""
        thermostat = Thermostat()
        thermostat.set_setpoint(20)
        thermostat.set_temp(18)
        self.assertTrue(thermostat.heating.is_set())

        thermostat.set_state_offline()
        self.assertFalse(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())

    def test_read_temp_offline(self):
        """Test that temperature reading raises error when thermostat is OFF"""
        thermostat = Thermostat()
        thermostat.set_state_offline()
        self.assertRaises(RuntimeError, thermostat.set_temp, 20)

    def test_heat_mode_no_cool(self):
        """Thermostat should not cool when in heat mode"""
        thermostat = Thermostat()
        thermostat.set_mode_heat()
        thermostat.set_cool_setpoint(25)
        thermostat.set_heat_setpoint(20)
        thermostat.set_temp(29)
        self.assertFalse(thermostat.cooling.is_set())
        self.assertFalse(thermostat.heating.is_set())

    def test_cool_mode_no_heat(self):
        """Thermostat should not heat when in cool mode"""
        thermostat = Thermostat()
        thermostat.set_mode_cool()
        thermostat.set_cool_setpoint(25)
        thermostat.set_heat_setpoint(20)
        thermostat.set_temp(15)
        self.assertFalse(thermostat.heating.is_set())
        self.assertFalse(thermostat.cooling.is_set())


class TestThermostatMemory(TestCase):
    def test_avg_temp_change(self):
        """Test average temperature change with multiple readings"""
        thermostat = Thermostat()
        thermostat.set_temp(20)
        thermostat.set_temp(22)
        thermostat.set_temp(21)
        thermostat.set_temp(23)

        # Average change should be (2 + -1 + 2) / 3 = 1.0
        self.assertEqual(thermostat.avg_temp_change, 1.0)

    def test_avg_temp_change_insufficient_data(self):
        """Test average temperature change with insufficient data"""
        thermostat = Thermostat()
        thermostat.set_temp(20)

        # With only one reading, average change should be 0.0
        self.assertEqual(thermostat.avg_temp_change, 0.0)

        # With two readings, we can calculate change
        thermostat.set_temp(22)
        self.assertEqual(thermostat.avg_temp_change, 2.0)

    def test_avg_temp_change_window(self):
        """Test average temperature change with time window"""
        # Simulate a time window of 1 minute
        thermostat = Thermostat(window_len=60)
        thermostat.set_temp(20)
        thermostat.set_temp(22)

        # Add a reading outside the window, 2 minutes ago
        thermostat._temps.append(TemperatureReading(18, mktime(localtime()) - (2 * 60)))

        # Average change should only consider the last two readings within the window
        self.assertEqual(thermostat.avg_temp_change, 2.0)

    def test_avg_temp_change_window_insufficient_data(self):
        """Test average temperature change with insufficient data in window"""
        thermostat = Thermostat(window_len=60)
        thermostat.set_temp(20)

        # With only one reading, average change should be 0.0
        self.assertEqual(thermostat.avg_temp_change, 0.0)

        # Add a reading outside the window, 2 minutes ago
        thermostat._temps.append(TemperatureReading(18, mktime(localtime()) - (2 * 60)))

        # Still only one valid reading in the window
        self.assertEqual(thermostat.avg_temp_change, 0.0)

    def test_avg_temp_change_window_multiple_readings(self):
        """Test average temperature change with multiple readings in window"""
        thermostat = Thermostat(window_len=60)
        thermostat.set_temp(20)
        thermostat.set_temp(22)
        thermostat.set_temp(21)

        # Add a reading outside the window, 2 minutes ago
        thermostat._temps.append(TemperatureReading(18, mktime(localtime()) - (2 * 60)))

        # Average change should only consider the last three readings within the window
        self.assertEqual(thermostat.avg_temp_change, (2 + -1) / 2)

    def test_queue_len_discards(self):
        """Temperature queue should discard readings when full"""
        thermostat = Thermostat(queue_len=3)
        thermostat.set_temp(20)
        thermostat.set_temp(22)
        thermostat.set_temp(21)
        thermostat.set_temp(23)

        # The first reading (20) should be discarded
        self.assertEqual(thermostat.avg_temp_change, (-1 + 2) / 2)

    def test_temp_history_full(self):
        """Temperature history should return readings in time order"""
        thermostat = Thermostat()

        # Manually add some readings in non-sorted order
        thermostat._temps.append(TemperatureReading(20, mktime(localtime()) - 5 * 60))
        thermostat._temps.append(TemperatureReading(22, mktime(localtime()) - 3 * 60))
        thermostat._temps.append(TemperatureReading(21, mktime(localtime()) - 1 * 60))
        thermostat._temps.append(TemperatureReading(23, mktime(localtime())))

        # Full history should return all readings in sorted order
        history = thermostat.temp_history(full=True)
        self.assertEqual(len(history), 4)
        self.assertEqual(history[0].value, 20)
        self.assertEqual(history[1].value, 22)
        self.assertEqual(history[2].value, 21)
        self.assertEqual(history[3].value, 23)

    def test_temp_history_window(self):
        """Temperature history should return readings within the time window"""
        thermostat = Thermostat(window_len=5 * 60)

        # Manually add some readings
        thermostat._temps.append(TemperatureReading(20, mktime(localtime()) - 10 * 60))
        thermostat._temps.append(TemperatureReading(22, mktime(localtime()) - 3 * 60))
        thermostat._temps.append(TemperatureReading(21, mktime(localtime()) - 1 * 60))
        thermostat._temps.append(TemperatureReading(23, mktime(localtime())))

        # History should only return readings within the last 5 minutes
        history = thermostat.temp_history(full=False)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].value, 22)
        self.assertEqual(history[1].value, 21)
        self.assertEqual(history[2].value, 23)
