"""Tests for Brink ventilation performance optimizations."""

from __future__ import annotations

from datetime import datetime

from custom_components.brink_ventilation.models import (
    BrinkAlert,
    BrinkAlertLevel,
    BrinkDeviceData,
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
