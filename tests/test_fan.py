"""Regression tests for fan state derived from ventilation levels."""

from unittest.mock import MagicMock

import pytest

from custom_components.brink_ventilation.fan import (
    BrinkHomeLevelFanEntity,
    BrinkHomeVentilationFanEntity,
)
from custom_components.brink_ventilation.models import BrinkDeviceData


@pytest.mark.parametrize(
    "entity_class", (BrinkHomeLevelFanEntity, BrinkHomeVentilationFanEntity)
)
@pytest.mark.parametrize(
    ("level_parameter", "expected_airflow", "expected_percentage"),
    (
        (None, None, None),
        ({}, None, None),
        ({"value": None}, None, None),
        ({"value": "invalid"}, None, None),
        ({"value": []}, None, None),
        ({"value": 0}, 30, 10),
        ({"value": "0"}, 30, 10),
        ({"value": "1"}, 90, 30),
        ({"value": "3"}, 300, 100),
        ({"value": "4"}, 120, 40),
    ),
)
def test_level_dependent_state(
    entity_class: type[BrinkHomeLevelFanEntity | BrinkHomeVentilationFanEntity],
    level_parameter: dict[str, object] | None,
    expected_airflow: int | None,
    expected_percentage: int | None,
) -> None:
    """Keep unknown levels distinct from level zero and retain independent data."""
    parameters: dict[str, dict[str, object]] = {
        "ventilation_mode_0_airflow": {"value": 30},
        "ventilation_mode_1_airflow": {"value": 90},
        "ventilation_mode_3_airflow": {"value": 300},
        "ventilation_mode_4_airflow": {"value": 120},
        "supply_air_flow_setpoint": {"value": 75},
    }
    if level_parameter is not None:
        parameters["ventilation_level"] = {
            "name": "Ventilation level",
            "default_value": "1",
            "options": [{"label": "Low"}],
            **level_parameter,
        }
    device = BrinkDeviceData(
        api_is_online=True,
        system_id=101,
        name="Test device",
        internal_name="Test device",
        model="Flair 300",
        serial_number="test-device",
        gateway_state="online",
        gateway_type_id=3,
        device_is_online=True,
        ip_address=None,
        dns_server=None,
        sw_version=None,
        alerts=[],
        parameters=parameters,
    )
    coordinator = MagicMock(data={101: device})
    fan = entity_class(MagicMock(), coordinator, 101)

    assert fan.werkt_percentage == expected_percentage
    attributes = fan.extra_state_attributes
    if expected_airflow is None:
        assert "airflow" not in attributes
    else:
        assert attributes["airflow"] == expected_airflow
    assert attributes["airflow_setpont"] == 75
    if level_parameter is not None:
        assert attributes["name"] == "Ventilation level"
        assert attributes["default_value"] == "1"
        assert attributes["raw_options"] == ["Low"]
