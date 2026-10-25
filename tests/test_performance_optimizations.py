"""Tests for Brink ventilation performance optimizations."""

from __future__ import annotations

from datetime import datetime

from unittest.mock import MagicMock

from custom_components.brink_ventilation.models import (
    BrinkAlert,
    BrinkAlertLevel,
    BrinkDeviceData,
)
from custom_components.brink_ventilation.sensor import (
    BrinkHomeSensorEntity,
    BrinkSensorDescription,
)


def test_brink_device_data_has_blocking_error_default():
    """Test that has_blocking_error defaults to False."""
    device = BrinkDeviceData(
        api_is_online=True,
        system_id=101,
        name="Test Device",
        internal_name="Test Device",
        model="Flair 300",
        serial_number="123456",
        gateway_state="online",
        gateway_type_id=3,
        device_is_online=True,
        ip_address="192.168.1.50",
        dns_server="192.168.1.1",
        sw_version="1.0.0",
        alerts=[],
        parameters={},
    )
    assert device.has_blocking_error is False


def test_brink_device_data_has_blocking_error_computed():
    """Test that has_blocking_error correctly reflects blocking alert state."""
    non_blocking_alert = BrinkAlert(
        id=1,
        component_id=10,
        code=100,
        level=BrinkAlertLevel.WARNING,
        is_active=True,
        is_archived=False,
        incoming=datetime.now(),
        outgoing=None,
        code_text="Warning",
        description="Non-blocking warning",
    )

    blocking_alert = BrinkAlert(
        id=2,
        component_id=10,
        code=101,
        level=BrinkAlertLevel.BLOCKING,
        is_active=True,
        is_archived=False,
        incoming=datetime.now(),
        outgoing=None,
        code_text="Error",
        description="Blocking error",
    )

    device_normal = BrinkDeviceData(
        api_is_online=True,
        system_id=101,
        name="Test Device",
        internal_name="Test Device",
        model="Flair 300",
        serial_number="123456",
        gateway_state="online",
        gateway_type_id=3,
        device_is_online=True,
        ip_address="192.168.1.50",
        dns_server="192.168.1.1",
        sw_version="1.0.0",
        alerts=[non_blocking_alert],
        parameters={},
        has_blocking_error=any(
            a.level == BrinkAlertLevel.BLOCKING for a in [non_blocking_alert]
        ),
    )
    assert device_normal.has_blocking_error is False

    device_blocked = BrinkDeviceData(
        api_is_online=True,
        system_id=101,
        name="Test Device",
        internal_name="Test Device",
        model="Flair 300",
        serial_number="123456",
        gateway_state="online",
        gateway_type_id=3,
        device_is_online=True,
        ip_address="192.168.1.50",
        dns_server="192.168.1.1",
        sw_version="1.0.0",
        alerts=[non_blocking_alert, blocking_alert],
        parameters={},
        has_blocking_error=any(
            a.level == BrinkAlertLevel.BLOCKING for a in [non_blocking_alert, blocking_alert]
        ),
    )
    assert device_blocked.has_blocking_error is True


def test_brink_device_data_system_attributes():
    """Test that system attributes are correctly stored on BrinkDeviceData."""
    device = BrinkDeviceData(
        api_is_online=True,
        system_id=101,
        name="Test Device",
        internal_name="Test Device",
        model="Flair 300",
        serial_number="123456",
        gateway_state="online",
        gateway_type_id=3,
        device_is_online=True,
        ip_address="192.168.1.50",
        dns_server="192.168.1.1",
        sw_version="1.0.0",
        alerts=[],
        parameters={},
        has_blocking_error=False,
        is_system_owner=True,
        is_editable=True,
        access_level=12,
        owner_group_name="Home",
        is_favorite=False,
        active_alert_count=0,
        iana_time_zone="Europe/Amsterdam",
        two_letter_country_code="NL",
        user_group_names=["Home"],
        total_count=1,
    )

    assert device.is_system_owner is True
    assert device.owner_group_name == "Home"
    assert device.iana_time_zone == "Europe/Amsterdam"
    assert device.two_letter_country_code == "NL"
    assert device.active_alert_count == 0
    assert device.access_level == 12


def test_device_attribute_sensor_availability():
    """Test availability logic for device attribute sensors."""
    device = BrinkDeviceData(
        api_is_online=True,
        system_id=101,
        name="Test Device",
        internal_name="Test Device",
        model="Flair 300",
        serial_number="123456",
        gateway_state="online",
        gateway_type_id=3,
        device_is_online=True,
        ip_address="192.168.1.50",
        dns_server="192.168.1.1",
        sw_version="1.0.0",
        alerts=[],
        parameters={},
        has_blocking_error=False,
        owner_group_name="Home Group",
    )

    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.data = {101: device}

    desc = BrinkSensorDescription(
        key="owner_group_name",
        translation_key="owner_group_name",
        parameter_key="owner_group_name",
        is_device_attribute=True,
    )

    entity = BrinkHomeSensorEntity(
        client=MagicMock(),
        coordinator=coordinator,
        system_id=101,
        description=desc,
    )

    assert entity.available is True
    assert entity.native_value == "Home Group"


def test_blocking_error_extra_attributes():
    """Test optimized extra state attributes for blocking error binary sensor."""
    from custom_components.brink_ventilation.binary_sensor import (
        BrinkBinarySensorDescription,
        BrinkHomeBinarySensorEntity,
        _get_blocking_error_extra_attributes,
    )

    now = datetime.now()
    warning_alert = BrinkAlert(
        id=1,
        component_id=10,
        code=100,
        level=BrinkAlertLevel.WARNING,
        is_active=True,
        is_archived=False,
        incoming=now,
        outgoing=None,
        code_text="Warning",
        description="Non-blocking warning",
    )

    coordinator = MagicMock()
    coordinator.active_alerts = [warning_alert]

    desc = BrinkBinarySensorDescription(
        key="blocking_error",
        translation_key="blocking_error",
        parameter_key="blocking_error",
        requires_parameter=False,
    )

    entity = BrinkHomeBinarySensorEntity(
        client=MagicMock(),
        coordinator=coordinator,
        system_id=101,
        description=desc,
    )

    assert entity._device is device
    assert entity.available is True

    # Empty coordinator data should return False without raising AttributeError
    coordinator.data = {}
    assert entity.available is False


def test_extract_parameters_options_maps():
    """Test that _extract_parameters pre-computes options_map and reverse_options_map."""
    from custom_components.brink_ventilation.core.brink_home_cloud import (
        BrinkHomeCloud,
    )

    nav_items = [
        {
            "parameterGroups": [
                {
                    "parameters": [
                        {
                            "id": 16012,
                            "name": "Betriebsart",
                            "value": "1",
                            "listItems": [
                                {"value": 0, "text": "Automatic", "isSelectable": True},
                                {"value": 1, "text": "Manual", "isSelectable": True},
                            ],
                        }
                    ]
                }
            ]
        }
    ]

    parameters = {}
    BrinkHomeCloud._extract_parameters(nav_items, parameters)

    assert "operating_mode" in parameters
    param = parameters["operating_mode"]
    assert param["options_map"] == {"0": "Automatic", "1": "Manual"}
    assert param["reverse_options_map"] == {"Automatic": "0", "Manual": "1"}


def test_select_and_sensor_options_map_lookup():
    """Test that select and sensor entities correctly use pre-computed options_map."""
    options = [
        {"value": "0", "label": "Auto"},
        {"value": "1", "label": "Manual"},
    ]
    options_map = {"0": "Auto", "1": "Manual"}
    reverse_options_map = {"Auto": "0", "Manual": "1"}

    device = BrinkDeviceData(
        api_is_online=True,
        system_id=101,
        name="Device 1",
        internal_name="Device 1",
        model="Flair 300",
        serial_number="101",
        gateway_state="online",
        gateway_type_id=3,
        device_is_online=True,
        ip_address="192.168.1.50",
        dns_server="192.168.1.1",
        sw_version="1.0.0",
        alerts=[],
        parameters={
            "operating_mode": {
                "value": "1",
                "value_state": 1,
                "options": options,
                "options_map": options_map,
                "reverse_options_map": reverse_options_map,
            }
        },
    )

    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.api_is_online = True
    coordinator.data = {101: device}

    select_desc = BrinkSelectEntityDescription(
        key="operating_mode",
        parameter_key="operating_mode",
    )
    select_entity = BrinkHomeSelectEntity(
        client=MagicMock(),
        coordinator=coordinator,
        system_id=101,
        description=select_desc,
    )

    assert select_entity.current_option == "Manual"

    sensor_desc = BrinkSensorDescription(
        key="operating_mode",
        parameter_key="operating_mode",
        is_enum=True,
    )
    sensor_entity = BrinkHomeSensorEntity(
        client=MagicMock(),
        coordinator=coordinator,
        system_id=101,
        description=sensor_desc,
    )

    assert sensor_entity.native_value == "Manual"
    attrs = _get_blocking_error_extra_attributes(entity)
    assert attrs["alert_count"] == 1
    assert attrs["highest_level"] == "WARNING"
    assert attrs["highest_level_value"] == int(BrinkAlertLevel.WARNING)
    assert len(attrs["alerts"]) == 1
    assert attrs["alerts"][0]["id"] == 1

    # Test empty alerts case
    coordinator.active_alerts = []
    attrs_empty = _get_blocking_error_extra_attributes(entity)
    assert attrs_empty["alert_count"] == 0
    assert attrs_empty["highest_level"] == "INFORMATION"
    assert attrs_empty["highest_level_value"] == int(BrinkAlertLevel.INFORMATION)
    assert attrs_empty["alerts"] == []
