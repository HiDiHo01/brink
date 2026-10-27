"""Tests for Brink ventilation performance optimizations."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from custom_components.brink_ventilation.binary_sensor import (
    _get_blocking_error_attributes,
)
from custom_components.brink_ventilation.models import (
    BrinkAlert,
    BrinkAlertLevel,
    BrinkDeviceData,
)
from custom_components.brink_ventilation.number import (
    BrinkHomeNumberEntity,
    BrinkNumberEntityDescription,
)
from custom_components.brink_ventilation.select import (
    BrinkHomeSelectEntity,
    BrinkSelectEntityDescription,
)
from custom_components.brink_ventilation.fan import (
    FAN_PRESET_MODES,
    BrinkHomeVentilationFanEntity,
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


def test_brink_select_description_reverse_label_map():
    """Test that reverse_label_map computes and caches correctly."""
    desc = BrinkSelectEntityDescription(
        key="test_select",
        parameter_key="test_param",
        label_map={"0": "Off", "1": "On", "2": "Auto"},
    )

    # First access computes the reverse label map
    reverse1 = desc.reverse_label_map
    assert reverse1 == {"Off": "0", "On": "1", "Auto": "2"}

    # Second access returns cached object instance
    reverse2 = desc.reverse_label_map
    assert reverse2 is reverse1


def test_brink_select_description_reverse_label_map_none():
    """Test reverse_label_map when label_map is None."""
    desc = BrinkSelectEntityDescription(
        key="test_select_none",
        parameter_key="test_param_none",
    )

    reverse1 = desc.reverse_label_map
    assert reverse1 == {}

    reverse2 = desc.reverse_label_map
    assert reverse2 is reverse1


def test_select_entity_availability_and_device_lookup():
    """Test BrinkHomeSelectEntity availability and O(1) device resolution."""
    device1 = BrinkDeviceData(
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
        parameters={"operating_mode": {"value": "0", "value_state": 1}},
    )

    device2 = BrinkDeviceData(
        api_is_online=True,
        system_id=102,
        name="Device 2",
        internal_name="Device 2",
        model="Flair 400",
        serial_number="102",
        gateway_state="online",
        gateway_type_id=3,
        device_is_online=True,
        ip_address="192.168.1.51",
        dns_server="192.168.1.1",
        sw_version="1.0.0",
        alerts=[],
        parameters={"operating_mode": {"value": "1", "value_state": 1}},
    )

    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.api_is_online = True
    coordinator.data = {101: device1, 102: device2}

    desc = BrinkSelectEntityDescription(
        key="operating_mode",
        parameter_key="operating_mode",
    )

    # System 102 entity should resolve to device2, not device1
    entity2 = BrinkHomeSelectEntity(
        client=MagicMock(),
        coordinator=coordinator,
        system_id=102,
        description=desc,
    )

    assert entity2._device is device2
    assert entity2.available is True

    # When coordinator data is None/empty, available returns False safely
    coordinator.data = None
    assert entity2.available is False


def test_number_entity_availability_and_device_lookup():
    """Test BrinkHomeNumberEntity availability and safe handling of empty data."""
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
        parameters={"bypass_temperature": {"value": "20", "value_state": 1}},
    )

    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.api_is_online = True
    coordinator.data = {101: device}

    desc = BrinkNumberEntityDescription(
        key="bypass_temperature",
        parameter_key="bypass_temperature",
    )

    entity = BrinkHomeNumberEntity(
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
                                {"value": 0, "text": "Auto Duplicate", "isSelectable": True},
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
    assert param["reverse_options_map"] == {
        "Automatic": "0",
        "Manual": "1",
        "Auto Duplicate": "0",
    }


def test_select_and_sensor_options_map_lookup():
    """Test that select and sensor entities correctly use pre-computed options_map even if options list is empty."""
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
                "options": [],  # Make options list empty to verify lookups use precomputed maps
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

    assert select_entity.current_option == "manual"

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

    assert sensor_entity.native_value == "manual"


def test_get_blocking_error_attributes_empty():
    """Test _get_blocking_error_attributes when no active alerts exist."""
    coordinator = MagicMock()
    coordinator.active_alerts = []
    entity = MagicMock(coordinator=coordinator)

    attrs = _get_blocking_error_attributes(entity)
    assert attrs == {
        "alert_count": 0,
        "highest_level": "INFORMATION",
        "highest_level_value": 0,
        "alerts": [],
    }


def test_get_blocking_error_attributes_with_alerts():
    """Test _get_blocking_error_attributes with active alerts of varying levels."""
    now = datetime.now()
    alert_info = BrinkAlert(
        id=1,
        component_id=10,
        code=101,
        level=BrinkAlertLevel.INFORMATION,
        is_active=True,
        is_archived=False,
        incoming=now,
        outgoing=None,
        code_text="Info",
        description="Info alert",
    )
    alert_blocking = BrinkAlert(
        id=2,
        component_id=10,
        code=102,
        level=BrinkAlertLevel.BLOCKING,
        is_active=True,
        is_archived=False,
        incoming=now,
        outgoing=None,
        code_text="Block",
        description="Blocking error alert",
    )

    coordinator = MagicMock()
    coordinator.active_alerts = [alert_info, alert_blocking]
    entity = MagicMock(coordinator=coordinator)

    attrs = _get_blocking_error_attributes(entity)
    assert attrs["alert_count"] == 2
    assert attrs["highest_level"] == "BLOCKING"
    assert attrs["highest_level_value"] == 3
    assert len(attrs["alerts"]) == 2
    assert attrs["alerts"][1]["code"] == 102
    assert attrs["alerts"][1]["level"] == "BLOCKING"
    assert attrs["alerts"][1]["level_value"] == 3


def test_fan_preset_modes_constant_reference():
    """Test that preset_modes returns the pre-allocated constant list instance."""
    coordinator = MagicMock()
    coordinator.data = {}

    fan = BrinkHomeVentilationFanEntity(
        client=MagicMock(),
        coordinator=coordinator,
        system_id=101,
    )

    preset_modes1 = fan.preset_modes
    preset_modes2 = fan.preset_modes

    assert preset_modes1 is FAN_PRESET_MODES
    assert preset_modes2 is FAN_PRESET_MODES


def test_fan_entity_safe_null_device_handling():
    """Test that fan properties safely return None/dict when device data is empty or None."""
    coordinator = MagicMock()
    coordinator.data = {}

    fan = BrinkHomeVentilationFanEntity(
        client=MagicMock(),
        coordinator=coordinator,
        system_id=101,
    )

    assert fan.percentage is None
    assert fan.werkt_percentage is None

    attrs = fan.extra_state_attributes
    assert isinstance(attrs, dict)
    assert attrs["key"] == "speed"
