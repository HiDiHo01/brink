from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant

from .const import (
    ACTIVE_CONTROL_STATUS_LABELS,
    BYPASS_VALVE_STATUS_LABELS,
    DATA_CLIENT,
    DATA_COORDINATOR,
    DOMAIN,
    FILTER_STATUS_LABELS,
    FROST_PROTECTION_STATUS_LABELS,
    GATEWAY_STATE_LABELS_STR,
    GEOTHERMAL_HEAT_EXCHANGER_LABELS,
    PARAM_ACTIVE_CONTROL_STATUS,
    PARAM_ACTUAL_SUPPLY_AIR_FLOW,
    PARAM_BYPASS_VALVE_STATUS,
    PARAM_CO2_SENSOR_1,
    PARAM_CO2_SENSOR_2,
    PARAM_CO2_SENSOR_3,
    PARAM_CO2_SENSOR_4,
    PARAM_DAYS_SINCE_FILTER_RESET,
    PARAM_DAYS_UNTIL_FILTER_MESSAGE,
    PARAM_EXHAUST_AIR_FLOW,
    PARAM_EXHAUST_AIR_PRESSURE,
    PARAM_EXHAUST_TEMP,
    PARAM_FILTER_MESSAGE,
    PARAM_FILTER_STATUS,
    PARAM_FRESH_AIR_TEMP,
    PARAM_FROST_PROTECTION_STATUS,
    PARAM_HUMIDITY,
    PARAM_NOMINAL_EXHAUST_AIR_FLOW,
    PARAM_NOMINAL_SUPPLY_AIR_FLOW,
    PARAM_PREHEATER_POWER,
    PARAM_PREHEATER_STATUS,
    PARAM_REMAINING_DURATION,
    PARAM_STATUS_GEOTHERMAL_HEAT_EXCHANGER,
    PARAM_SUPPLY_AIR_FLOW,
    PARAM_SUPPLY_AIR_PRESSURE,
    PARAM_SUPPLY_TEMP,
    PARAM_VENTILATION_MODE_0,
    PARAM_VENTILATION_MODE_1,
    PARAM_VENTILATION_MODE_2,
    PARAM_VENTILATION_MODE_3,
    PREHEATER_STATUS_LABELS,
)
from .entity import BrinkHomeDeviceEntity

_LOGGER = logging.getLogger(__name__)
REVOLUTIONS_PER_MINUTE = "rpm"


@dataclass(frozen=True)
class BrinkSensorDescription(SensorEntityDescription):
    """Describe a Brink sensor entity."""

    parameter_key: str = ""
    is_enum: bool = False
    is_device_attribute: bool = False
    required_value_state: int | None = None
    value_map: dict[str, str] | None = None
    enabled_value_state: int | None = None
    _attr_has_entity_name = True


SENSOR_DESCRIPTIONS: tuple[BrinkSensorDescription, ...] = (
    BrinkSensorDescription(
        key="ventilation_level",
        translation_key="ventilation_level",
        parameter_key="ventilation_level",
        icon="mdi:fan",
    ),
    BrinkSensorDescription(
        key=PARAM_SUPPLY_AIR_FLOW,
        translation_key="actual_supply_air_flow",
        parameter_key=PARAM_SUPPLY_AIR_FLOW,
        icon="mdi:fan-chevron-up",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key=PARAM_ACTUAL_SUPPLY_AIR_FLOW,
        translation_key="actual_supply_air_flow",
        parameter_key=PARAM_ACTUAL_SUPPLY_AIR_FLOW,
        icon="mdi:fan-chevron-up",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key=PARAM_EXHAUST_AIR_FLOW,
        translation_key="actual_exhaust_air_flow",
        parameter_key=PARAM_EXHAUST_AIR_FLOW,
        icon="mdi:fan-chevron-down",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key=PARAM_NOMINAL_SUPPLY_AIR_FLOW,
        translation_key="nominal_supply_air_flow",
        parameter_key=PARAM_NOMINAL_SUPPLY_AIR_FLOW,
        icon="mdi:fan-chevron-up",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key=PARAM_NOMINAL_EXHAUST_AIR_FLOW,
        translation_key="nominal_exhaust_air_flow",
        parameter_key=PARAM_NOMINAL_EXHAUST_AIR_FLOW,
        icon="mdi:fan-chevron-down",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key=PARAM_FRESH_AIR_TEMP,
        translation_key="fresh_air_temp",
        parameter_key=PARAM_FRESH_AIR_TEMP,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key="extract_air_temperature",
        translation_key="extract_air_temperature",
        parameter_key="extract_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key=PARAM_EXHAUST_TEMP,
        translation_key="exhaust_temp",
        parameter_key=PARAM_EXHAUST_TEMP,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key=PARAM_SUPPLY_TEMP,
        translation_key="supply_temp",
        parameter_key=PARAM_SUPPLY_TEMP,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key=PARAM_HUMIDITY,
        translation_key="humidity",
        parameter_key=PARAM_HUMIDITY,
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        required_value_state=1,
    ),
    BrinkSensorDescription(
        key="supply_air_humidity",
        translation_key="supply_air_humidity",
        parameter_key="supply_air_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key="extract_air_humidity",
        translation_key="extract_air_humidity",
        parameter_key="extract_air_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key="relative_humidity",
        translation_key="relative_humidity",
        parameter_key="relative_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        required_value_state=1,
    ),
    BrinkSensorDescription(
        key=PARAM_DAYS_SINCE_FILTER_RESET,
        translation_key="days_since_filter_reset",
        parameter_key=PARAM_DAYS_SINCE_FILTER_RESET,
        icon="mdi:air-filter",
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key=PARAM_DAYS_UNTIL_FILTER_MESSAGE,
        translation_key="days_until_filter_message",
        parameter_key=PARAM_DAYS_UNTIL_FILTER_MESSAGE,
        icon="mdi:air-filter",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="filter_message",
        translation_key="filter_message",
        parameter_key=PARAM_FILTER_MESSAGE,
        icon="mdi:air-filter",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key=PARAM_REMAINING_DURATION,
        translation_key="remaining_duration",
        parameter_key=PARAM_REMAINING_DURATION,
        icon="mdi:timer-sand",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key=PARAM_ACTIVE_CONTROL_STATUS,
        translation_key="active_control_status",
        parameter_key=PARAM_ACTIVE_CONTROL_STATUS,
        icon="mdi:tune",
        device_class=SensorDeviceClass.ENUM,
        is_enum=True,
        value_map=ACTIVE_CONTROL_STATUS_LABELS,
        entity_registry_enabled_default=True,
    ),
    BrinkSensorDescription(
        key=PARAM_PREHEATER_STATUS,
        translation_key="preheater_status",
        parameter_key=PARAM_PREHEATER_STATUS,
        icon="mdi:radiator",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_enum=True,
        required_value_state=1,
        value_map=PREHEATER_STATUS_LABELS,
    ),
    BrinkSensorDescription(
        key=PARAM_BYPASS_VALVE_STATUS,
        translation_key="bypass_valve_status",
        parameter_key=PARAM_BYPASS_VALVE_STATUS,
        icon="mdi:call-split",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_enum=True,
        value_map=BYPASS_VALVE_STATUS_LABELS,
    ),
    BrinkSensorDescription(
        key=PARAM_CO2_SENSOR_1,
        translation_key="co2_sensor_1",
        parameter_key=PARAM_CO2_SENSOR_1,
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        enabled_value_state=1,
        icon="mdi:molecule-co2",
        entity_registry_enabled_default=False,
    ),
    BrinkSensorDescription(
        key=PARAM_CO2_SENSOR_2,
        translation_key="co2_sensor_2",
        parameter_key=PARAM_CO2_SENSOR_2,
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        enabled_value_state=1,
        icon="mdi:molecule-co2",
        entity_registry_enabled_default=False,
    ),
    BrinkSensorDescription(
        key=PARAM_CO2_SENSOR_3,
        translation_key="co2_sensor_3",
        parameter_key=PARAM_CO2_SENSOR_3,
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        enabled_value_state=1,
        icon="mdi:molecule-co2",
        entity_registry_enabled_default=False,
    ),
    BrinkSensorDescription(
        key=PARAM_CO2_SENSOR_4,
        translation_key="co2_sensor_4",
        parameter_key=PARAM_CO2_SENSOR_4,
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        enabled_value_state=1,
        icon="mdi:molecule-co2",
        entity_registry_enabled_default=False,
    ),
    BrinkSensorDescription(
        key="extra_air_temp",
        translation_key="extra_air_temp",
        parameter_key="extra_air_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    BrinkSensorDescription(
        key="additional_temperature_sensor",
        translation_key="additional_temperature_sensor",
        parameter_key="additional_temperature_sensor",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    BrinkSensorDescription(
        key=PARAM_FILTER_STATUS,
        translation_key="filter_status",
        parameter_key=PARAM_FILTER_STATUS,
        icon="mdi:air-filter",
        device_class=SensorDeviceClass.ENUM,
        is_enum=True,
        value_map=FILTER_STATUS_LABELS,
    ),
    BrinkSensorDescription(
        key=PARAM_FROST_PROTECTION_STATUS,
        translation_key="frost_protection_status",
        parameter_key=PARAM_FROST_PROTECTION_STATUS,
        icon="mdi:snowflake-alert",
        device_class=SensorDeviceClass.ENUM,
        is_enum=True,
        value_map=FROST_PROTECTION_STATUS_LABELS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key=PARAM_STATUS_GEOTHERMAL_HEAT_EXCHANGER,
        translation_key="status_geothermal_heat_exchanger",
        parameter_key=PARAM_STATUS_GEOTHERMAL_HEAT_EXCHANGER,
        icon="mdi:heat-pump",
        device_class=SensorDeviceClass.ENUM,
        is_enum=True,
        value_map=GEOTHERMAL_HEAT_EXCHANGER_LABELS,
    ),
    BrinkSensorDescription(
        key="analog_input_1",
        translation_key="analog_input_1",
        parameter_key="analog_input_1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    BrinkSensorDescription(
        key="analog_input_2",
        translation_key="analog_input_2",
        parameter_key="analog_input_2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    BrinkSensorDescription(
        key="supply_air_pressure",
        translation_key="supply_air_pressure",
        parameter_key=PARAM_SUPPLY_AIR_PRESSURE,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key="exhaust_air_pressure",
        translation_key="exhaust_air_pressure",
        parameter_key=PARAM_EXHAUST_AIR_PRESSURE,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key="supply_air_flow_setpoint",
        translation_key="supply_air_flow_setpoint",
        parameter_key="supply_air_flow_setpoint",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-chevron-up",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="exhaust_air_flow_setpoint",
        translation_key="exhaust_air_flow_setpoint",
        parameter_key="exhaust_air_flow_setpoint",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-chevron-down",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="nominal_supply_air_flow",
        translation_key="nominal_supply_air_flow",
        parameter_key="nominal_supply_air_flow",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-chevron-down",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="nominal_exhaust_air_flow",
        translation_key="nominal_exhaust_air_flow",
        parameter_key="nominal_exhaust_air_flow",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-chevron-up",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="ventilation_percentage",
        translation_key="ventilation_percentage",
        parameter_key="ventilation_percentage",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BrinkSensorDescription(
        key="v1_analog_input",
        translation_key="v1_analog_input",
        parameter_key="v1_analog_input",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    BrinkSensorDescription(
        key="v2_analog_input",
        translation_key="v2_analog_input",
        parameter_key="v2_analog_input",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    BrinkSensorDescription(
        key="ventilation_mode_0_airflow",
        translation_key="ventilation_mode_0_airflow",
        parameter_key=PARAM_VENTILATION_MODE_0,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="ventilation_mode_1_airflow",
        translation_key="ventilation_mode_1_airflow",
        parameter_key=PARAM_VENTILATION_MODE_1,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-speed-1",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="ventilation_mode_2_airflow",
        translation_key="ventilation_mode_2_airflow",
        parameter_key=PARAM_VENTILATION_MODE_2,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-speed-2",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="ventilation_mode_3_airflow",
        translation_key="ventilation_mode_3_airflow",
        parameter_key=PARAM_VENTILATION_MODE_3,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-speed-3",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="supply_duct_pressure",
        translation_key="supply_duct_pressure",
        parameter_key="supply_duct_pressure",
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="exhaust_duct_pressure",
        translation_key="exhaust_duct_pressure",
        parameter_key="exhaust_duct_pressure",
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="supply_fan_rpm",
        translation_key="supply_fan_rpm",
        parameter_key="supply_fan_rpm",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="exhaust_fan_rpm",
        translation_key="exhaust_fan_rpm",
        parameter_key="exhaust_fan_rpm",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BrinkSensorDescription(
        key="preheater_power",
        translation_key="preheater_power",
        parameter_key=PARAM_PREHEATER_POWER,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radiator",
        entity_registry_enabled_default=False,
    ),
    BrinkSensorDescription(
        key="gateway_state",
        translation_key="gateway_state",
        parameter_key="gateway_state",
        icon="mdi:lan",
        device_class=SensorDeviceClass.ENUM,
        options=list(GATEWAY_STATE_LABELS_STR.values()),
        is_enum=True,
        is_device_attribute=True,
        value_map=GATEWAY_STATE_LABELS_STR,
    ),
)


def _should_create_sensor(device: dict, description: BrinkSensorDescription) -> bool:
    """Return True when the Brink parameter should be exposed as a sensor."""

    if description.parameter_key == "ventilation_percentage":
        return True

    if description.is_device_attribute:
        return True

    param = device.get("parameters", {}).get(description.parameter_key)

    if not param:
        return False

    if param.get("valueState") == 5:
        return False

    # CO2 sensors are only available when the value is not 0, otherwise they are not connected
    if description.parameter_key in {
        PARAM_CO2_SENSOR_1,
        PARAM_CO2_SENSOR_2,
        PARAM_CO2_SENSOR_3,
        PARAM_CO2_SENSOR_4,
    }:
        return str(param.get("value")) != "0"

    required_value_state = description.required_value_state
    if required_value_state is None:
        return True

    return param.get("value_state") == required_value_state


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the Brink sensor platform."""
    client = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    known_parameters = {
        description.parameter_key
        for description in SENSOR_DESCRIPTIONS
    }

    known_parameters.add("supply_air_pressure")
    # device
    known_parameters.add("device_type")
    known_parameters.add("software_label")
    # fan
    known_parameters.add("ventilation_level")
    known_parameters.add("operating_mode")
    # select
    known_parameters.add("bypass_operation")
    known_parameters.add("signal_output_mode")

    known_parameters.add("contact_1_type")
    known_parameters.add("contact_2_type")

    known_parameters.add("cn1_switch_input_condition")
    known_parameters.add("cn2_switch_input_condition")

    known_parameters.add("contact_1_supply_fan_action")
    known_parameters.add("contact_1_exhaust_fan_action")
    known_parameters.add("contact_2_supply_fan_action")
    known_parameters.add("contact_2_exhaust_fan_action")

    known_parameters.add("mode_input_1")
    known_parameters.add("mode_input_2")

    known_parameters.add("mode_valve_24v_control")
    known_parameters.add("valve_control")
    known_parameters.add("rh_sensor_sensitivity")

    # number
    known_parameters.add("bypass_temperature")
    known_parameters.add("bypass_hysteresis")
    known_parameters.add("minimum_intake_temperature")
    known_parameters.add("imbalance_fireplace")
    known_parameters.add("v1_minimum_voltage")
    known_parameters.add("v1_maximum_voltage")
    known_parameters.add("v2_minimum_voltage")
    known_parameters.add("v2_maximum_voltage")
    known_parameters.add("switch_temp_1")
    known_parameters.add("switch_temp_2")

    known_parameters.add("co2_sensor_1_min_ppm")
    known_parameters.add("co2_sensor_1_max_ppm")
    known_parameters.add("co2_sensor_2_min_ppm")
    known_parameters.add("co2_sensor_2_max_ppm")
    known_parameters.add("co2_sensor_3_min_ppm")
    known_parameters.add("co2_sensor_3_max_ppm")
    known_parameters.add("co2_sensor_4_min_ppm")
    known_parameters.add("co2_sensor_4_max_ppm")

    # Binary
    known_parameters.add("cn1_switch_input")
    known_parameters.add("cn2_switch_input")

    known_parameters.add("rh_sensor_status")
    known_parameters.add("ebus_co2_sensor_status")

    for system_id, device in (coordinator.data or {}).items():
        for key, param in device.get("parameters", {}).items():
            if key not in known_parameters:
                _LOGGER.info(
                    "Unhandled parameter key=%s name=%s value=%s "
                    "control_type=%s read_write=%s options=%s",
                    key,
                    param.get("name"),
                    param.get("value"),
                    param.get("control_type"),
                    param.get("read_write"),
                    len(param.get("options", [])),
                )

    entities = [
        BrinkHomeSensorEntity(client, coordinator, system_id, description)
        for system_id, device in (coordinator.data or {}).items()
        for description in SENSOR_DESCRIPTIONS
        if _should_create_sensor(device, description)
    ]
    async_add_entities(entities)


class BrinkHomeSensorEntity(BrinkHomeDeviceEntity, SensorEntity):
    """Representation of a Brink sensor."""

    _attr_has_entity_name = True
    entity_description: BrinkSensorDescription

    def __init__(self, client, coordinator, system_id: int, description: BrinkSensorDescription):
        """Initialize the Brink sensor."""
        super().__init__(client, coordinator, system_id, description.parameter_key)
        self.entity_description = description
#         _LOGGER.warning(
#             "translation_key=%s",
#             self.entity_description.translation_key,
#         )

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.system_id}_{self.parameter_key}_sensor"

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""
        if self.entity_description.parameter_key == "ventilation_percentage":
            return {}

        param = self.data or {}

        attributes = {
            "key": str(self.entity_description.key),
            "translation_key": str(self.entity_description.translation_key),
            "name": str(param.get("name")),
            "raw_name": str(param.get("raw_name")),
            "value": str(param.get("value")),
            "value_state": param.get("value_state"),
            "default_value": str(param.get("default_value")),  # remove
            "numeric_id": str(param.get("numeric_id")),
            "read_write": param.get("read_write"),
            "control_type": param.get("control_type"),
            "value_id": str(param.get("value_id")),
            "min_value": str(param.get("min_value")),  # remove
            "max_value": str(param.get("max_value")),  # remove
            "step_width": str(param.get("step_width")),  # remove
            "decimals": str(param.get("decimals")),
            "list_items": param.get("list_items"),  # remove
            "unit_of_measure": str(param.get("unit_of_measure")),
            "component_id": str(param.get("component_id")),
            "raw_options": param.get("options"),  # remove
        }

        if param.get("options"):
            attributes["raw_options"] = [
                option.get("label")
                for option in param.get("options", [])
            ]

        return attributes

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the native unit of measurement."""
        if (
            self.entity_description.native_unit_of_measurement
            is not None
        ):
            return str(
                self.entity_description.native_unit_of_measurement
            )

        param = self.data

        if param is None:
            return None

        unit = param.get("unit_of_measure")

        if not unit:
            return None

        return str(unit)

    @property
    def options(self) -> list[str] | None:
        if not self.entity_description.is_enum:
            return None

        value_map = self.entity_description.value_map
        if value_map is not None:
            return list(value_map.values())

        param = self.data
        if param is None:
            return None
        return [item["label"] for item in param.get("options", [])]

    @property
    def entity_registry_enabled_default(self) -> bool:
        enabled_value_state = self.entity_description.enabled_value_state
        if enabled_value_state is None:
            return super().entity_registry_enabled_default

        param = self.data
        if param is None:
            return False

        return param.get("value_state") == enabled_value_state

    @property
    def _raw_value(self) -> object | None:
        """Return the raw sensor value."""

        if self.entity_description.is_device_attribute:
            device = self._device

            if device is None:
                return None
            return device.get(self.parameter_key)

        param = self.data

        if param is None:
            return None

        return param.get("value")

    @property
    def native_value(self) -> str | int | float | None:
        """Return the sensor value."""

        if self.parameter_key == "ventilation_percentage":
            return self._calculate_ventilation_percentage()

        _LOGGER.debug(
            "gateway_state raw=%s",
            self._raw_value,
        )

        value = self._raw_value

        if value is None:
            return None

        if self.entity_description.is_enum:
            value_map = self.entity_description.value_map

            if value_map is not None:
                _LOGGER.debug(
                    "gateway_state value=%s mapped=%s options=%s",
                    value,
                    value_map.get(str(value), str(value)),
                    self.options,
                )
                return value_map.get(str(value), "unknown")

            param = self.data

            if param is not None:
                selected = next(
                    (
                        item["label"]
                        for item in param.get("options", [])
                        if item["value"] == str(value)
                    ),
                    None,
                )

                if selected is not None:
                    return selected

            return str(value)

        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)

        return int(number) if number.is_integer() else number

    @property
    def old_native_value(self):
        if self.parameter_key == "ventilation_percentage":
            return self._calculate_ventilation_percentage()

        param = self.data
        if param is None:
            return None

        value = param.get("value")
        if value is None:
            return None

        if self.entity_description.is_enum:
            value_map = self.entity_description.value_map
            if value_map is not None:
                return value_map.get(str(value), str(value))

            selected = next(
                (item["label"] for item in param.get("options", []) if item["value"] == str(value)),
                None,
            )
            return selected or str(value)

        try:
            number = float(value)
        except (TypeError, ValueError):
            return value

        if number.is_integer():
            return int(number)
        return number

    @property
    def available(self) -> bool:
        """Return if entity is available."""

        _LOGGER.debug(
            "gateway_state available: super=%s data=%s raw=%s",
            super().available,
            self.data,
            self._raw_value,
        )

        if self.entity_description.parameter_key == "ventilation_percentage":
            return True

        if self.entity_description.parameter_key == "gateway_state":
            return True

        param = self.data

        return (
            super().available
            and param is not None
            and param.get("value_state") != 5
        )

    def _calculate_ventilation_percentage(self) -> int | None:
        """Calculate ventilation percentage based on configured airflow levels."""
        parameters = self._device.get("parameters", {})

        try:
            supply_flow = float(
                parameters["actual_supply_air_flow"]["value"]
            )
            exhaust_flow = float(
                parameters["actual_exhaust_air_flow"]["value"]
            )

            airflow_0 = float(
                parameters["ventilation_mode_0_airflow"]["value"]
            )
            airflow_1 = float(
                parameters["ventilation_mode_1_airflow"]["value"]
            )
            airflow_2 = float(
                parameters["ventilation_mode_2_airflow"]["value"]
            )
            airflow_3 = float(
                parameters["ventilation_mode_3_airflow"]["value"]
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return None

        current_flow = (
            supply_flow
            + exhaust_flow
        ) / 2

        levels = [
            (airflow_0, 0.0),
            (airflow_1, 33.333),
            (airflow_2, 66.667),
            (airflow_3, 100.0),
        ]

        if current_flow <= levels[0][0]:
            return 0

        if current_flow >= levels[-1][0]:
            return 100

        for index in range(len(levels) - 1):
            lower_flow, lower_percent = levels[index]
            upper_flow, upper_percent = levels[index + 1]
            upper_flow = 300  # do not use airflow_3 as max, use 300 for 100%

            if lower_flow <= current_flow <= upper_flow:
                if upper_flow == lower_flow:
                    return round(upper_percent)

                fraction = (
                    (current_flow - lower_flow)
                    / (upper_flow - lower_flow)
                )

                percentage = (
                    lower_percent
                    + (
                        fraction
                        * (upper_percent - lower_percent)
                    )
                )

                return round(percentage)

        return None
