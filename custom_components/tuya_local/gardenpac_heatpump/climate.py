"""
Garden PAC InverTech Swimming Pool Heatpump device.
"""
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    HVAC_MODE_HEAT,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    STATE_UNAVAILABLE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

from ..device import TuyaLocalDevice
from .const import (
    ATTR_OPERATING_MODE,
    ATTR_POWER_LEVEL,
    ATTR_TARGET_TEMPERATURE,
    ATTR_TEMP_UNIT,
    HVAC_MODE_TO_DPS_MODE,
    PRESET_MODE_TO_DPS_MODE,
    PROPERTY_TO_DPS_ID,
)

SUPPORT_FLAGS = SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE


class GardenPACPoolHeatpump(ClimateEntity):
    """Representation of a GardenPAC InverTech Heatpump WiFi pool heater."""

    def __init__(self, device):
        """Initialize the heater.
        Args:
            device (TuyaLocalDevice): The device API instance."""
        self._device = device

        self._support_flags = SUPPORT_FLAGS

        self._TEMPERATURE_STEP = 1
        self._TEMPERATURE_LIMITS = {"min": 18, "max": 45}

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._device.name

    @property
    def unique_id(self):
        """Return the unique id for this heater."""
        return self._device.unique_id

    @property
    def device_info(self):
        """Return device information about this heater."""
        return self._device.device_info

    @property
    def icon(self):
        """Return the icon to use in the frontend for this device."""
        hvac_mode = self.hvac_mode

        if hvac_mode == HVAC_MODE_HEAT:
            return "mdi:hot-tub"
        else:
            return "mdi:radiator-disabled"

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        dps_unit = self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_TEMP_UNIT])
        if dps_unit:
            return TEMP_CELSIUS
        else:
            return TEMP_FAHRENHEIT

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_TARGET_TEMPERATURE])

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return self._TEMPERATURE_STEP

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._TEMPERATURE_LIMITS["min"]

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._TEMPERATURE_LIMITS["max"]

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            await self.async_set_target_temperature(kwargs.get(ATTR_TEMPERATURE))

    async def async_set_target_temperature(self, target_temperature):
        target_temperature = int(round(target_temperature))

        limits = self._TEMPERATURE_LIMITS
        if not limits["min"] <= target_temperature <= limits["max"]:
            raise ValueError(
                f"Target temperature ({target_temperature}) must be between "
                f'{limits["min"]} and {limits["max"]}.'
            )

        await self._device.async_set_property(
            PROPERTY_TO_DPS_ID[ATTR_TARGET_TEMPERATURE], target_temperature
        )

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_TEMPERATURE])

    @property
    def hvac_mode(self):
        """Return current HVAC mode, ie Heat or Off."""
        dps_mode = self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_HVAC_MODE])

        if dps_mode is not None:
            return TuyaLocalDevice.get_key_for_value(HVAC_MODE_TO_DPS_MODE, dps_mode)
        else:
            return STATE_UNAVAILABLE

    @property
    def hvac_modes(self):
        """Return the list of available HVAC modes."""
        return list(HVAC_MODE_TO_DPS_MODE.keys())

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new HVAC mode."""
        dps_mode = HVAC_MODE_TO_DPS_MODE[hvac_mode]
        await self._device.async_set_property(
            PROPERTY_TO_DPS_ID[ATTR_HVAC_MODE], dps_mode
        )

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        dps_preset = self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_PRESET_MODE])
        if dps_preset is not None:
            return TuyaLocalDevice.get_key_for_value(
                PRESET_MODE_TO_DPS_MODE, dps_preset
            )
        else:
            return None

    @property
    def preset_modes(self):
        """Return the list of available preset modes"""
        return list(PRESET_MODE_TO_DPS_MODE.keys())

    async def async_set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        dps_mode = PRESET_MODE_TO_DPS_MODE[preset_mode]
        await self._device.async_set_property(
            PROPERTY_TO_DPS_ID[ATTR_PRESET_MODE], dps_mode
        )

    @property
    def device_state_attributes(self):
        """Get additional attributes that HA doesn't naturally support."""
        power_level = self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_POWER_LEVEL])

        operating_mode = self._device.get_property(
            PROPERTY_TO_DPS_ID[ATTR_OPERATING_MODE]
        )

        return {ATTR_POWER_LEVEL: power_level, ATTR_OPERATING_MODE: operating_mode}

    async def async_update(self):
        await self._device.async_refresh()
