from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from .const import (
    DATA_CLIENT,
    DATA_COORDINATOR,
    DOMAIN,
    GATEWAY_STATE_LABELS,
    GATEWAY_STATE_ONLINE,
    PARAM_CN1_POSITION,
    PARAM_CN1_SWITCH_INPUT,
    PARAM_CN2_POSITION,
    PARAM_CN2_SWITCH_INPUT,
    PARAM_CO1_SENSOR_STATUS,
    PARAM_CO2_SENSOR_STATUS,
    PARAM_FILTER_STATUS,
    PARAM_RH_SENSOR_STATUS,
)
from .entity import BrinkHomeDeviceEntity

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BrinkBinarySensorDescription(
    BinarySensorEntityDescription
):
    """Describe a Brink binary sensor."""
    parameter_key: str
    data_fn: Callable[[dict[str, object] | None], dict[str, object] | None] | None = None
    value_fn: Callable[[dict[str, object]], bool | None] | None = None
    attr_fn: Callable[[dict[str, object]], dict[str, object] | None] | None = None
    icon_fn: Callable[[bool | None], str | None] | None = None
    available_fn: Callable[
        [dict[str, object]],
        bool | None,
    ] | None = None


class BrinkHomeBinarySensorEntity(
    BrinkHomeDeviceEntity,
    BinarySensorEntity,
):
    """Representation of a Brink binary sensor."""

    _attr_has_entity_name = True

    entity_description: BrinkBinarySensorDescription

    def __init__(
        self,
        client,
        coordinator,
        system_id: int,
        description: BrinkBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(
            client,
            coordinator,
            system_id,
            description.parameter_key,
        )
        self.entity_description = description

    @property
    def old_unique_id(self) -> str:
        """Return a unique ID."""
        return (
            f"{DOMAIN}_{self.system_id}_"
            f"{self.parameter_key}_binary_sensor"
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return (
            f"{DOMAIN}_{self.system_id}_"
            f"{self.entity_description.key}"
        )

    @property
    def icon(self) -> str | None:
        """Return the entity icon."""

        if self.entity_description.icon_fn is not None:
            return self.entity_description.icon_fn(self.is_on)

        return self.entity_description.icon

    @property
    def is_on(self) -> bool | None:
        """Return sensor state."""

        _LOGGER.debug(
            "Gateway data for %s: %s",
            self.system_id,
            self._entity_data,
        )

        data = self._entity_data

        if data is None:
            return None

        if self.entity_description.value_fn is not None:
            result = self.entity_description.value_fn(data)

            if self.entity_description.key == "gateway_state":
                _LOGGER.debug(
                    "Gateway state=%s online=%s result=%s",
                    data.get("value"),
                    GATEWAY_STATE_ONLINE,
                    result,
                )

            return result

        value = data.get("value")

        if value is None:
            return None

        return str(value) == "1"

    @property
    def available(self) -> bool:
        """Return if entity is available."""

        data = self._entity_data

        if data is None:
            return False

        # Override availability for system/device entities.
        if self.entity_description.available_fn is not None:
            return bool(self.entity_description.available_fn(data))

        return (
            super().available
            and (
                data.get("value_state") is None
                or data.get("value_state") != 5
            )
        )

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""

        data = self._entity_data or {}

        attributes = {
            "key": _debug_value(self.entity_description.key),
            "translation_key": _debug_value(self.entity_description.translation_key),
            "name": _debug_value(data.get("name")),
            "raw_name": _debug_value(data.get("raw_name")),
            "value": _debug_value(data.get("value")),
            "value_state": _debug_value(data.get("value_state")),
            "default_value": _debug_value(data.get("default_value")),
            "numeric_id": _debug_value(data.get("numeric_id")),
            "read_write": _debug_value(data.get("read_write")),
            "control_type": _debug_value(data.get("control_type")),
            "value_id": _debug_value(data.get("value_id")),
            "list_items": _debug_value(data.get("list_items")),
            "component_id": _debug_value(data.get("component_id")),
            "options": data.get("options"),
            "options_str": _debug_value(data.get("options")),
        }

        # binary sensors should not have this keys but if they do they are in the wrong sensor section (select or number)
        for key in (
            "min_value",
            "max_value",
            "step_width",
            "decimals",
            "unit_of_measure",
        ):
            if data.get(key) is not None:
                attributes[key] = data[key]

        if self.entity_description.attr_fn is not None:
            attributes: dict[str, object] = {
                "key": _debug_value(self.entity_description.key),
                "translation_key": _debug_value(self.entity_description.translation_key),
                "value": _debug_value(data.get("value"))
            }
            custom_attributes = self.entity_description.attr_fn(data)

            if custom_attributes:
                attributes.update(custom_attributes)
                # attributes = custom_attributes

        return attributes

    @property
    def _entity_data(self) -> dict[str, object] | None:
        """Return the data source for this entity."""

        if self.entity_description.data_fn is not None:
            return self.entity_description.data_fn(self._device)

        return self.data


def _debug_value(value: object) -> str:
    """Convert a value to a debug-friendly string."""
    return str(value)


BINARY_SENSOR_DESCRIPTIONS: tuple[BrinkBinarySensorDescription, ...] = (
    BrinkBinarySensorDescription(
        key="gateway_status",
        translation_key="gateway_status",
        parameter_key="gateway_status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        data_fn=lambda device: (
            {
                "value": device.get("gateway_state"),
                "device_is_online": device.get("device_is_online"),
                "gateway_type_id": device.get("gateway_type_id"),
            }
            if device is not None
            else None
        ),
        value_fn=lambda data: bool(str(data.get("value")) == str(GATEWAY_STATE_ONLINE)),
        attr_fn=lambda data: {
            "gateway_state": data.get("value"),
            "device_is_online": data.get("device_is_online"),
            "gateway_type_id": data.get("gateway_type_id"),
            "gateway_state_label": GATEWAY_STATE_LABELS.get(
                int(data.get("value", -1)),
                "unknown",
            ),
        },
        icon_fn=lambda is_on: (
            "mdi:connection"
            if is_on
            else "mdi:lan-disconnect"
        ),
        available_fn=lambda data: True
    ),
    BrinkBinarySensorDescription(
        key="device_online",
        translation_key="device_online",
        parameter_key="device_online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        data_fn=lambda device: (
            {
                "value": device.get("device_is_online"),
            }
            if device is not None
            else None
        ),
        value_fn=lambda data: data.get("value"),
        icon_fn=lambda is_on: (
            "mdi:connection"
            if is_on
            else "mdi:lan-disconnect"
        ),
        available_fn=lambda data: True
    ),
    BrinkBinarySensorDescription(
        key=PARAM_FILTER_STATUS,
        translation_key="filter_need_change",
        parameter_key=PARAM_FILTER_STATUS,
        icon="mdi:air-filter",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda param: str(param.get("value")) == "1",
    ),
    BrinkBinarySensorDescription(
        key=PARAM_RH_SENSOR_STATUS,
        translation_key="rh_sensor_status",
        parameter_key=PARAM_RH_SENSOR_STATUS,
        icon="mdi:water-percent",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BrinkBinarySensorDescription(
        key=PARAM_CO1_SENSOR_STATUS,
        translation_key="co1_sensor_status",
        parameter_key=PARAM_CO1_SENSOR_STATUS,
        icon="mdi:molecule-co2",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkBinarySensorDescription(
        key=PARAM_CO2_SENSOR_STATUS,
        translation_key="co2_sensor_status",
        parameter_key=PARAM_CO2_SENSOR_STATUS,
        icon="mdi:molecule-co2",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkBinarySensorDescription(
        key="ebus_co2_sensor_status",
        translation_key="ebus_co2_sensor_status",
        parameter_key="ebus_co2_sensor_status",
        icon="mdi:molecule-co2",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        available_fn=lambda data: True,
        entity_registry_enabled_default=False,
    ),
    BrinkBinarySensorDescription(
        key="cn1_position",
        translation_key="cn1_position",
        parameter_key=PARAM_CN1_POSITION,
        icon="mdi:electric-switch",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkBinarySensorDescription(
        key="cn2_position",
        translation_key="cn2_position",
        parameter_key=PARAM_CN2_POSITION,
        icon="mdi:electric-switch",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkBinarySensorDescription(
        key="cn1_switch_input",
        translation_key="cn1_switch_input",
        parameter_key=PARAM_CN1_SWITCH_INPUT,
        icon="mdi:electric-switch",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BrinkBinarySensorDescription(
        key="cn2_switch_input",
        translation_key="cn2_switch_input",
        parameter_key=PARAM_CN2_SWITCH_INPUT,
        icon="mdi:electric-switch",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up Brink binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]

    entities = []

    for system_id, device in (coordinator.data or {}).items():
        for description in BINARY_SENSOR_DESCRIPTIONS:
            if description.data_fn is not None:
                entities.append(
                    BrinkHomeBinarySensorEntity(
                        client,
                        coordinator,
                        system_id,
                        description,
                    )
                )
                continue

            parameters = device.get("parameters", {})
            _LOGGER.debug(
                "ebus_co2_sensor_status exists=%s value=%s",
                "ebus_co2_sensor_status" in parameters,
                parameters.get("ebus_co2_sensor_status"),
            )
            if parameters.get(description.parameter_key) is not None:
                entities.append(
                    BrinkHomeBinarySensorEntity(
                        client,
                        coordinator,
                        system_id,
                        description,
                    )
                )

    async_add_entities(entities)


def _gateway_state_value(device: dict | None) -> int | None:
    """Normalize the Brink gateway state."""
    if device is None:
        return None

    state = device.get("gateway_state")
    try:
        return state
    except (TypeError, ValueError):
        return None
