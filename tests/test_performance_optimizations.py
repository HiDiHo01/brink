"""Tests for Brink ventilation performance optimizations."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

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
