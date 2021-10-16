from homeassistant.components.climate.const import (
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import STATE_UNAVAILABLE, TEMP_CELSIUS, TEMP_FAHRENHEIT

from ..const import KOGAN_KAWFPAC09YA_AIRCON_PAYLOAD
from ..helpers import assert_device_properties_set
from .base_device_tests import TuyaDeviceTestCase

POWER_DPS = "1"
TEMPERATURE_DPS = "2"
CURRENTTEMP_DPS = "3"
HVACMODE_DPS = "4"
FAN_DPS = "5"
UNIT_DPS = "19"
COUNTDOWN_DPS = "105"
UNKNOWN106_DPS = "106"
UNKNOWN107_DPS = "107"


class TestKoganKAWFPAC09YA(TuyaDeviceTestCase):
    __test__ = True

    def setUp(self):
        self.setUpForConfig(
            "kogan_kawfpac09ya_airconditioner.yaml",
            KOGAN_KAWFPAC09YA_AIRCON_PAYLOAD,
        )
        self.subject = self.entities.get("climate")

    def test_supported_features(self):
        self.assertEqual(
            self.subject.supported_features,
            SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE,
        )

    def test_icon(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "COOL"
        self.assertEqual(self.subject.icon, "mdi:snowflake")
        self.dps[HVACMODE_DPS] = "DRY"
        self.assertEqual(self.subject.icon, "mdi:water")
        self.dps[HVACMODE_DPS] = "FAN"
        self.assertEqual(self.subject.icon, "mdi:fan")
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.icon, "mdi:hvac-off")

    def test_temperature_unit(self):
        self.dps[UNIT_DPS] = "C"
        self.assertEqual(self.subject.temperature_unit, TEMP_CELSIUS)
        self.dps[UNIT_DPS] = "F"
        self.assertEqual(self.subject.temperature_unit, TEMP_FAHRENHEIT)

    def test_target_temperature(self):
        self.dps[TEMPERATURE_DPS] = 25
        self.assertEqual(self.subject.target_temperature, 25)

    def test_target_temperature_step(self):
        self.assertEqual(self.subject.target_temperature_step, 1)

    def test_minimum_target_temperature(self):
        self.dps[UNIT_DPS] = "C"
        self.assertEqual(self.subject.min_temp, 16)
        self.dps[UNIT_DPS] = "F"
        self.assertEqual(self.subject.min_temp, 60)

    def test_maximum_target_temperature(self):
        self.dps[UNIT_DPS] = "C"
        self.assertEqual(self.subject.max_temp, 30)
        self.dps[UNIT_DPS] = "F"
        self.assertEqual(self.subject.max_temp, 86)

    async def test_legacy_set_temperature_with_temperature(self):
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 24}
        ):
            await self.subject.async_set_temperature(temperature=24)

    async def test_legacy_set_temperature_with_no_valid_properties(self):
        await self.subject.async_set_temperature(something="else")
        self.subject._device.async_set_property.assert_not_called()

    async def test_set_target_temperature_succeeds_within_valid_range(self):
        async with assert_device_properties_set(
            self.subject._device,
            {TEMPERATURE_DPS: 25},
        ):
            await self.subject.async_set_target_temperature(25)

    async def test_set_target_temperature_rounds_value_to_closest_integer(self):
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 23}
        ):
            await self.subject.async_set_target_temperature(22.6)

    async def test_set_target_temperature_fails_outside_valid_range(self):
        with self.assertRaisesRegex(
            ValueError, "temperature \\(15\\) must be between 16 and 30"
        ):
            await self.subject.async_set_target_temperature(15)

        with self.assertRaisesRegex(
            ValueError, "temperature \\(31\\) must be between 16 and 30"
        ):
            await self.subject.async_set_target_temperature(31)

    def test_current_temperature(self):
        self.dps[CURRENTTEMP_DPS] = 25
        self.assertEqual(self.subject.current_temperature, 25)

    def test_hvac_mode(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "COOL"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_COOL)

        self.dps[HVACMODE_DPS] = "DRY"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_DRY)

        self.dps[HVACMODE_DPS] = "FAN"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_FAN_ONLY)

        self.dps[HVACMODE_DPS] = None
        self.assertEqual(self.subject.hvac_mode, STATE_UNAVAILABLE)

        self.dps[HVACMODE_DPS] = "FAN"
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_OFF)

    def test_hvac_modes(self):
        self.assertCountEqual(
            self.subject.hvac_modes,
            [
                HVAC_MODE_OFF,
                HVAC_MODE_COOL,
                HVAC_MODE_DRY,
                HVAC_MODE_FAN_ONLY,
            ],
        )

    async def test_turn_on(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: True, HVACMODE_DPS: "COOL"}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_COOL)

    async def test_turn_off(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: False}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_OFF)

    def test_fan_mode(self):
        self.dps[FAN_DPS] = "1"
        self.assertEqual(self.subject.fan_mode, "low")
        self.dps[FAN_DPS] = "2"
        self.assertEqual(self.subject.fan_mode, "high")

    def test_fan_modes(self):
        self.assertCountEqual(
            self.subject.fan_modes,
            [
                "low",
                "high",
            ],
        )

    async def test_set_fan_mode_to_low(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: "1"},
        ):
            await self.subject.async_set_fan_mode("low")

    async def test_set_fan_mode_to_high(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: "2"},
        ):
            await self.subject.async_set_fan_mode("high")

    def test_device_state_attribures(self):
        self.dps[COUNTDOWN_DPS] = 105
        self.dps[UNKNOWN106_DPS] = 106
        self.dps[UNKNOWN107_DPS] = True
        self.assertDictEqual(
            self.subject.device_state_attributes,
            {
                "countdown": 105,
                "unknown_106": 106,
                "unknown_107": True,
            },
        )