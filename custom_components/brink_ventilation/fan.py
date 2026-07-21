from __future__ import annotations

import logging
from dataclasses import dataclass

import voluptuous as vol
from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_platform

from .const import (
    DATA_CLIENT,
    DATA_COORDINATOR,
    DOMAIN,
    FAN_OPERATING_MODE_LABELS,
    MODE_MANUAL_VALUE,
    PARAM_OPERATING_MODE,
    PARAM_VENTILATION_LEVEL,
)
from .entity import BrinkHomeDeviceEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_ON_PERCENTAGE = 33

OPERATING_MODE_LABELS_REVERSE = {
    label: value
    for value, label in FAN_OPERATING_MODE_LABELS.items()
}


@dataclass(frozen=True, kw_only=True)
class BrinkFanEntityDescription(FanEntityDescription):
    """Describe a Brink fan entity."""

    parameter_key: str


VENTILATION_FAN_DESCRIPTION = BrinkFanEntityDescription(
    key="ventilation",
    translation_key="ventilation",
    parameter_key=PARAM_VENTILATION_LEVEL,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities
) -> None:
    """Set up the Brink ventilation fan platform."""
    client = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "set_level",
        {
            vol.Required("level"): vol.All(
                vol.Coerce(int),
                vol.In([0, 1, 2, 3]),
            )
        },
        "async_set_level",
    )

    platform.async_register_entity_service(
        "set_airflow",
        {"airflow": int},
        "async_set_airflow",
    )

    entities = [
        BrinkHomeVentilationFanEntity(client, coordinator, system_id)
        for system_id, device in (coordinator.data or {}).items()
        if device.get("parameters", {}).get(PARAM_VENTILATION_LEVEL)
    ]
    async_add_entities(entities)


class BrinkHomeVentilationFanEntity(BrinkHomeDeviceEntity, FanEntity):
    """Representation of the Brink ventilation level control."""

    _attr_has_entity_name = True

    entity_description: BrinkFanEntityDescription = (
        VENTILATION_FAN_DESCRIPTION
    )

    def __init__(
        self,
        client,
        coordinator,
        system_id: int,
    ) -> None:
        """Initialize the fan."""
        super().__init__(
            client,
            coordinator,
            system_id,
            self.entity_description.parameter_key,
        )
        self._attr_unique_id = (
            f"{DOMAIN}_{system_id}_{self.parameter_key}_fan"
        )
        self._max_airflow = 300
        self._level_0_max = 50
        self._level_1_max = 133
        self._level_2_max = 216
        self._level_3_max = 300
        device = next(iter((self.coordinator.data or {}).values()), {})
        parameters = device.get("parameters", {})
        ventilation = self.data or {}
        level = int(ventilation.get("value", 0))
        airflow_param = (
            device["parameters"]
            .get(f"ventilation_mode_{level}_airflow", {})
        )

        self._current_airflow = (
            parameters.get("supply_air_flow_setpoint", {})
            .get("value")
        )

    async def async_set_airflow(
        self,
        airflow: int,
    ) -> None:
        """Set airflow."""

        _LOGGER.warning(
            "async_set_airflow called with airflow=%s",
            airflow,
        )

        await self.async_set_percentage(
            round(airflow / self._max_airflow * 100)
        )

    async def async_set_level(
        self,
        level: int,
    ) -> None:
        """Set ventilation level."""

        if level not in (0, 1, 2, 3):
            raise HomeAssistantError(
                f"Invalid ventilation level: {level}"
            )

        await self._async_write_level(str(level))

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed percentage."""

        target_airflow = round(
            percentage / 100 * self._max_airflow
        )

        if target_airflow <= 50:
            level = 0
        elif target_airflow <= self._level_1_max:
            level = 1
        elif target_airflow <= self._level_2_max:
            level = 2
        else:
            level = 3

        _LOGGER.debug(
            "Requested percentage=%s target_airflow=%s level=%s",
            percentage,
            target_airflow,
            level,
        )

        await self._set_airflow_for_level(
            level=level,
            airflow=target_airflow,
        )

        await self._async_write_level(str(level))

    async def _set_airflow_for_level(
        self,
        level: int,
        airflow: int,
    ) -> None:
        """Set airflow for a ventilation level."""

        device = next(iter((self.coordinator.data or {}).values()), {})
        parameters = device.get("parameters", {})

        parameter = parameters.get(
            f"ventilation_mode_{level}_airflow"
        )

        if parameter is None or parameter.get("value_id") is None:
            raise HomeAssistantError(
                f"Airflow parameter for level {level} is unavailable"
            )

        min_value = int(parameter.get("min_value") or 0)
        max_value = int(parameter.get("max_value") or airflow)

        airflow = max(
            min_value,
            min(airflow, max_value),
        )

        params = [
            (
                int(parameter["value_id"]),
                str(airflow),
            )
        ]

        _LOGGER.debug(
            "Writing airflow params: %s",
            params,
        )

        await self.client.write_parameters(
            self.system_id,
            params,
        )

        parameter["value"] = str(airflow)

        self.coordinator.async_set_updated_data(
            dict(self.coordinator.data)
        )
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

        _LOGGER.debug(
            "Ventilation level=%s airflow=%s",
            level,
            airflow,
        )

    async def _async_write_level(self, level_value: str) -> None:
        ventilation = self.data
        if ventilation is None or ventilation.get("value_id") is None:
            raise HomeAssistantError("Ventilation parameter is unavailable")

        params = []
        mode = self._operating_mode

        if mode and mode.get("value_id") is not None:
            _LOGGER.debug(
                "Switching operating mode to manual due to fan speed change"
            )
            params.append((int(mode["value_id"]), MODE_MANUAL_VALUE))
        params.append((int(ventilation["value_id"]), level_value))

        _LOGGER.debug(
            "Writing fan params: %s",
            params,
        )

        await self.client.write_parameters(self.system_id, params)
        ventilation["value"] = level_value
        if mode is not None:
            mode["value"] = MODE_MANUAL_VALUE
        self.coordinator.async_set_updated_data(dict(self.coordinator.data))
        await self.coordinator.async_request_refresh()

        _LOGGER.debug(
            "Operating mode=%s ventilation=%s",
            mode.get("value") if mode else None,
            ventilation.get("value"),
        )

    @property
    def preset_modes(self) -> list[str]:
        """Return available preset modes."""
        # Fan preset modes currently do not support frontend translations.
        # Use translation keys to stay aligned with SelectEntity translations
        # and future Home Assistant support.
        return list(FAN_OPERATING_MODE_LABELS.values())

    @property
    def preset_mode(self) -> str | None:
        mode = self._operating_mode

        if mode is None:
            return None

        return FAN_OPERATING_MODE_LABELS.get(str(mode.get("value")))

    async def async_set_preset_mode(
        self,
        preset_mode: str,
    ) -> None:
        """Set the preset mode."""
        mode = self._operating_mode

        if mode is None or mode.get("value_id") is None:
            raise HomeAssistantError(
                "Operating mode parameter unavailable"
            )

        selected_value = OPERATING_MODE_LABELS_REVERSE.get(
            preset_mode
        )

        if selected_value is None:
            raise HomeAssistantError(
                f"Unknown preset mode: {preset_mode}"
            )

        await self.client.write_parameters(
            self.system_id,
            [(int(mode["value_id"]), selected_value)],
        )

        mode["value"] = selected_value

        await self.coordinator.async_request_refresh()

    @property
    def old_percentage(self) -> int | None:
        """Return current fan percentage."""
        device = next(iter((self.coordinator.data or {}).values()), {})
        parameters = device.get("parameters", {})

        airflow = (
            parameters.get("supply_air_flow_setpoint", {})
            .get("value")
        )

        if airflow is None:
            return None

        return round(int(airflow) / self._max_airflow * 100)

    @property
    def werkt_percentage(self) -> int | None:
        level = int((self.data or {}).get("value", 0))

        device = self._device or {}
        parameters = device.get("parameters", {})

        airflow = (
            parameters.get(
                f"ventilation_mode_{level}_airflow",
                {},
            ).get("value")
        )

        if airflow is None:
            return None

        _LOGGER.debug(
            "percentage airflow=%s",
            airflow,
        )

        return round(int(airflow) / self._max_airflow * 100)

    @property
    def percentage(self) -> int | None:
        """Return current fan percentage."""

        param = self.data or {}

        try:
            level = int(param.get("value", 0))
        except (TypeError, ValueError):
            return None

        device = self._device or {}
        parameters = device.get("parameters", {})

        airflow = (
            parameters.get(
                f"ventilation_mode_{level}_airflow",
                {},
            ).get("value")
        )

        try:
            airflow_value = int(airflow)
        except (TypeError, ValueError):
            return None

        _LOGGER.debug(
            "percentage=%s airflow=%s",
            round(int(airflow) / self._max_airflow * 100),
            airflow,
        )

        return round(
            airflow_value / self._max_airflow * 100
        )

    @property
    def percentage_step(self) -> float:
        """Return percentage step."""
        return 1

    @property
    def supported_features(self) -> FanEntityFeature:
        """Return supported features."""
        return (
            FanEntityFeature.TURN_OFF
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.SET_SPEED
            | FanEntityFeature.PRESET_MODE
        )

    @property
    def is_on(self) -> bool | None:
        param = self.data
        if param is None or param.get("value") is None:
            return None
        try:
            return int(param["value"]) != 0
        except (TypeError, ValueError):
            return None

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs,
    ) -> None:
        """Turn on the fan."""
        _LOGGER.debug(
            "Setting fan percentage=%s speed=%s preset_mode=%s",
            percentage,
            preset_mode,
        )

        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
            return

#        if percentage is None:
#            percentage = ranged_value_to_percentage(
#                SPEED_RANGE,
#                1,
#            )
#        await self.async_set_percentage(percentage)
        if percentage is None:
            await self._async_write_level("1")
            return

        await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_write_level("0")

    @property
    def _operating_mode(self) -> dict | None:
        """Return the operating mode parameter."""
        if self._device is None:
            return None

        return self._device.get(
            "parameters",
            {},
        ).get(PARAM_OPERATING_MODE)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""

        coordinator_data = self.coordinator.data or {}
        attributes = dict(super().extra_state_attributes or {})

        param = self.data or {}

        _LOGGER.debug(
            "Coordinator data: %s",
            self.coordinator.data,
        )

        _LOGGER.debug(
            "supply_air_flow_setpoint=%s",
            (self.coordinator.data or {}).get("supply_air_flow_setpoint"),
        )

        _LOGGER.debug(
            "Entity data keys: %s",
            list((self.data or {}).keys()),
        )
        # Entity data keys: ['name', 'raw_name', 'value', 'value_id', 'value_state', 'read_write', 'control_type', 'list_items', 'min_value', 'max_value', 'default_value', 'step_width', 'decimals', 'unit_of_measure', 'unit_of_measure1', 'unit_of_measure2', 'component_id', 'numeric_id', 'options']

        attributes.update(
            {
                "key": str(self.entity_description.key),
                "translation_key": str(self.entity_description.translation_key),
                "name": str(param.get("name")),
                "raw_name": str(param.get("raw_name")),
                "value": str(param.get("value")),
                "value_state": param.get("value_state"),
                "numeric_id": str(param.get("numeric_id")),
                "read_write": param.get("read_write"),
                "control_type": param.get("control_type"),
                "value_id": str(param.get("value_id")),
                "list_items": param.get("list_items"),
                "component_id": str(param.get("component_id")),
            }
        )

        device = self._device
        parameters = device.get("parameters", {})
        level = int(param.get("value", 0))
        airflow_param = (
            parameters.get(f"ventilation_mode_{level}_airflow", {})
        )

        attributes["airflow"] = airflow_param.get("value")
        airflow_setpoint = (
            parameters.get("supply_air_flow_setpoint", {})
            .get("value")
        )
        attributes["airflow_setpont"] = airflow_setpoint

        if param.get("default_value") is not None:
            attributes["default_value"] = str(param["default_value"])

        if param.get("options"):
            attributes["raw_options"] = [
                option.get("label")
                for option in param.get("options", [])
            ]

        return attributes
