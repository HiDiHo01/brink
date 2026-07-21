from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CN_SWITCH_INPUT_CONDITION_LABELS,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DOMAIN,
    FILTER_FAULT_CONDITION_LABELS,
    PARAM_BYPASS_FUNCTION,
    PARAM_BYPASS_OPERATION,
    PARAM_CN1_SWITCH_INPUT_CONDITION,
    PARAM_CN2_SWITCH_INPUT_CONDITION,
    PARAM_CONTACT_1_EXHAUST_FAN_ACTION,
    PARAM_CONTACT_2_EXHAUST_FAN_ACTION,
    PARAM_MODE_VALVE_24V_CONTROL,
    PARAM_OPERATING_MODE,
    PARAM_RH_SENSOR_SENSITIVITY,
    PARAM_SIGNAL_OUTPUT_MODE,
    PARAM_VALVE_CONTROL,
    PARAM_VENTILATION_LEVEL,
    RH_SENSOR_SENSITIVITY_LABELS,
)
from .entity import BrinkHomeDeviceEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BrinkSelectEntityDescription(SelectEntityDescription):
    """Describe a Brink select entity."""

    parameter_key: str
    label_map: Mapping[str, str] | None = None

    @property
    def reverse_label_map(self) -> dict[str, str]:
        """Return reverse label mapping."""
        return (
            {
                label: value
                for value, label in self.label_map.items()
            }
            if self.label_map
            else {}
        )


SELECT_DESCRIPTIONS: tuple[BrinkSelectEntityDescription, ...] = (
    BrinkSelectEntityDescription(
        key="operating_mode",
        translation_key="operating_mode",
        parameter_key=PARAM_OPERATING_MODE,
        icon="mdi:fan-auto",
    ),
    BrinkSelectEntityDescription(
        key="bypass_operation",
        translation_key="bypass_operation",
        parameter_key=PARAM_BYPASS_OPERATION,
        icon="mdi:swap-horizontal",
    ),
    BrinkSelectEntityDescription(
        key="ventilation_level",
        translation_key="ventilation_level",
        parameter_key=PARAM_VENTILATION_LEVEL,
        icon="mdi:fan",
    ),
    BrinkSelectEntityDescription(
        key="bypass_function",
        translation_key="bypass_function",
        parameter_key=PARAM_BYPASS_FUNCTION,
        icon="mdi:tune",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="mode_valve_24v_control",
        translation_key="mode_valve_24v_control",
        parameter_key=PARAM_MODE_VALVE_24V_CONTROL,
        icon="mdi:valve-open",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="valve_control",
        translation_key="valve_control",
        parameter_key=PARAM_VALVE_CONTROL,
        icon="mdi:valve",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="signal_output_mode",
        translation_key="signal_output_mode",
        parameter_key=PARAM_SIGNAL_OUTPUT_MODE,
        label_map=FILTER_FAULT_CONDITION_LABELS,
        icon="mdi:export-variant",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="cn1_conditions",
        translation_key="cn1_conditions",
        parameter_key="cn1_conditions",
        icon="mdi:connection",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="cn2_conditions",
        translation_key="cn2_conditions",
        parameter_key="cn2_conditions",
        icon="mdi:connection",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="mode_input_1",
        translation_key="mode_input_1",
        parameter_key="mode_input_1",
        icon="mdi:import",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="mode_input_2",
        translation_key="mode_input_2",
        parameter_key="mode_input_2",
        icon="mdi:import",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="contact_1_type",
        translation_key="contact_1_type",
        parameter_key="contact_1_type",
        icon="mdi:electric-switch",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="contact_1_supply_fan_action",
        translation_key="contact_1_supply_fan_action",
        parameter_key="contact_1_supply_fan_action",
        icon="mdi:fan",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="contact_1_exhaust_fan_action",
        translation_key="contact_1_exhaust_fan_action",
        parameter_key=PARAM_CONTACT_1_EXHAUST_FAN_ACTION,
        icon="mdi:fan",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="contact_2_type",
        translation_key="contact_2_type",
        parameter_key="contact_2_type",
        icon="mdi:electric-switch",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="contact_2_supply_fan_action",
        translation_key="contact_2_supply_fan_action",
        parameter_key="contact_2_supply_fan_action",
        icon="mdi:fan",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="contact_2_exhaust_fan_action",
        translation_key="contact_2_exhaust_fan_action",
        parameter_key=PARAM_CONTACT_2_EXHAUST_FAN_ACTION,
        icon="mdi:fan",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="supply_fan_control",
        translation_key="supply_fan_control",
        parameter_key="supply_fan_control",
        icon="mdi:fan",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="cn1_switch_input_condition",
        translation_key="cn1_switch_input_condition",
        parameter_key=PARAM_CN1_SWITCH_INPUT_CONDITION,
        label_map=CN_SWITCH_INPUT_CONDITION_LABELS,
        icon="mdi:connection",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="cn2_switch_input_condition",
        translation_key="cn2_switch_input_condition",
        parameter_key=PARAM_CN2_SWITCH_INPUT_CONDITION,
        label_map=CN_SWITCH_INPUT_CONDITION_LABELS,
        icon="mdi:connection",
        entity_category=EntityCategory.CONFIG,
    ),
    BrinkSelectEntityDescription(
        key="rh_sensor_sensitivity",
        translation_key="rh_sensor_sensitivity",
        parameter_key=PARAM_RH_SENSOR_SENSITIVITY,
        label_map=RH_SENSOR_SENSITIVITY_LABELS,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:water-percent",
    )
)


class BrinkHomeSelectEntity(BrinkHomeDeviceEntity, SelectEntity):
    """Base Brink select entity."""

    _attr_has_entity_name = True

    entity_description: BrinkSelectEntityDescription

    def __init__(
        self,
        client,
        coordinator,
        system_id: int,
        description: BrinkSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(
            client,
            coordinator,
            system_id,
            description.parameter_key,
        )
        self.entity_description = description

    async def _async_write_value(self, value: str) -> None:
        """Write a value to the Brink device."""
        param = self.data

        if param is None or param.get("value_id") is None:
            raise HomeAssistantError(
                f"{self.parameter_name} parameter is unavailable"
            )

        await self.client.write_parameters(
            self.system_id,
            [(int(param["value_id"]), value)],
        )

        param["value"] = value

        self.coordinator.async_set_updated_data(
            dict(self.coordinator.data)
        )

        await self.coordinator.async_request_refresh()

    @property
    def icon(self) -> str | None:
        """Return the entity icon."""

        if self.entity_description.key == PARAM_VENTILATION_LEVEL:
            value = str((self.data or {}).get("value", ""))

            return {
                "0": "mdi:fan-off",
                "1": "mdi:fan-speed-1",
                "2": "mdi:fan-speed-2",
                "3": "mdi:fan-speed-3",
            }.get(value, "mdi:fan")

        return self.entity_description.icon

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""
        param = self.data or {}

        return {
            "key": self.entity_description.key,
            "translation_key": self.entity_description.translation_key,
            "name": param.get("name", "onbeschikbaar"),
            "raw_name": param.get("raw_name", "onbeschikbaar"),
            "value": param.get("value", "onbeschikbaar"),
            "value_state": param.get("value_state", "onbeschikbaar"),
            "default_value": param.get("default_value", "onbeschikbaar"),
            "numeric_id": param.get("numeric_id", "onbeschikbaar"),
            "read_write": param.get("read_write", "onbeschikbaar"),
            "control_type": param.get("control_type", "onbeschikbaar"),
            "value_id": param.get("value_id", "onbeschikbaar"),
            "min_value": param.get("min_value", "onbeschikbaar"),
            "max_value": param.get("max_value", "onbeschikbaar"),
            "step_width": param.get("step_width", "onbeschikbaar"),
            "decimals": param.get("decimals", "onbeschikbaar"),
            "unit_of_measure": param.get("unit_of_measure", "onbeschikbaar"),
            "component_id": param.get("component_id", "onbeschikbaar"),
            "raw_options": param.get("options", "onbeschikbaar"),
        }

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return (
            f"{DOMAIN}_{self.system_id}_"
            f"{self.parameter_key}_select"
        )

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Select an option."""
        param = self.data

        if param is None:
            raise HomeAssistantError(
                f"{self.parameter_name} parameter is unavailable"
            )

        reverse_label_map = self.entity_description.reverse_label_map

        if reverse_label_map:
            selected_value = reverse_label_map.get(option)
        else:
            selected_value = next(
                (
                    item["value"]
                    for item in param.get("options", [])
                    if item["label"] == option
                ),
                None,
            )

        if selected_value is None:
            raise HomeAssistantError(
                f"Unknown option '{option}' "
                f"for {self.parameter_name}"
            )

        await self._async_write_value(str(selected_value))

    @property
    def old_current_option(self) -> str | None:
        """Return the currently selected option."""
        param = self.data

        if param is None:
            return None

        current_value = str(param.get("value"))

        label_map = self.entity_description.label_map

        if label_map:
            return label_map.get(current_value, current_value)

        return next(
            (
                option["label"]
                for option in param.get("options", [])
                if option["value"] == current_value
            ),
            None,
        )

    @property
    def current_option(self) -> str | None:
        """Return current option."""
        param = self.data

        if param is None:
            return None

        current_value = str(param.get("value"))

        label_map = self.entity_description.label_map

        if label_map:
            result = label_map.get(current_value)

            # _LOGGER.warning(
            #     "Select label map %s current=%r value=%r",
            #     self.parameter_key,
            #     result,
            #     current_value,
            # )

            return result

        return next(
            (
                option["label"]
                for option in param.get("options", [])
                if option["value"] == current_value
            ),
            None,
        )

    @property
    def old_options(self) -> list[str]:
        """Return available options."""
        param = self.data

        if param is None:
            return []

        if self.entity_description.label_map:
            return list(
                self.entity_description.label_map.values()
            )

        return [
            option["label"]
            for option in param.get("options", [])
        ]

    @property
    def options(self) -> list[str]:
        """Return available options."""

        label_map = self.entity_description.label_map

        if label_map:
            result = list(label_map.values())
            # _LOGGER.debug(
            #     "Select %s options=%r",
            #     self.parameter_key,
            #     result,
            # )
            return result

        param = self.data

        if param is None:
            return []

        return [
            str(option["label"])
            for option in param.get("options", [])
        ]

    @property
    def available(self) -> bool:
        """Return if entity is available."""

        device = next(iter((self.coordinator.data or {}).values()), {})
        parameters = device.get("parameters", {})

        _LOGGER.debug(
            "gateway_state available: super=%s data=%s current_value=%s",
            super().available,
            self.data,
            self.current_option,
        )

        if self.entity_description.parameter_key == "rh_sensor_sensitivity":
            rh_sensor = int(
                parameters.get("ebus_co2_sensor_status", {})
                .get("value")
            )
            return (rh_sensor == 1)

        param = self.data

        return (
            super().available
            and param is not None
            and param.get("value_state") != 5
        )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the Brink select platform."""
    client = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    entities = [
        BrinkHomeSelectEntity(
            client,
            coordinator,
            system_id,
            description,
        )
        for system_id, device in (coordinator.data or {}).items()
        for description in SELECT_DESCRIPTIONS
        if device.get("parameters", {}).get(
            description.parameter_key
        )
    ]

    async_add_entities(entities)
