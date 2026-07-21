"""Base entity support for Brink ventilation."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_MODEL, DEFAULT_NAME, DOMAIN


class BrinkHomeSystemEntity(CoordinatorEntity):
    """Common entity helpers for a Brink system."""

    def __init__(self, client, coordinator, system_id: int) -> None:
        """Initialize the Brink system entity."""
        super().__init__(coordinator)
        self.client = client
        self.system_id = system_id

    @property
    def _device(self) -> dict[str, object] | None:
        """Return the current device payload."""
        data = self.coordinator.data or {}
        return data.get(self.system_id)

    @property
    def device_name(self) -> str:
        """Return the Brink system display name."""
        device = self._device

        if device is None:
            return DEFAULT_NAME

        name = device.get("name")

        return str(name) if name is not None else DEFAULT_NAME

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the Brink entity."""
        device = self._device or {}
        return DeviceInfo(
            identifiers={(DOMAIN, str(self.system_id))},
            name=device.get("model", self.device_name), # use device model as device title in UI
            manufacturer=DEFAULT_NAME,
            model=device.get("model", DEFAULT_MODEL),
            serial_number=device.get("serial_number"),
            sw_version=device.get("sw_version"),
        )

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return self.coordinator.last_update_success and self._device is not None


class BrinkHomeDeviceEntity(BrinkHomeSystemEntity):
    """Common entity helpers for a Brink system parameter."""

    def __init__(self, client, coordinator, system_id: int, parameter_key: str) -> None:
        """Initialize the Brink parameter entity."""
        super().__init__(client, coordinator, system_id)
        self.parameter_key = parameter_key

    @property
    def data(self) -> dict[str, object] | None:
        """Return the current parameter payload."""
        parameter = self._parameters.get(self.parameter_key)

        return parameter if isinstance(parameter, dict) else None

    @property
    def _parameters(self) -> dict[str, object]:
        """Return the device parameters."""
        device = self._device

        if device is None:
            return {}

        parameters = device.get("parameters")

        return parameters if isinstance(parameters, dict) else {}

    @property
    def parameter_name(self) -> str:
        """Return the translated parameter name."""
        param = self.data

        default_name = self.parameter_key.replace("_", " ")

        if param is None:
            return default_name

        name = param.get("name")

        return str(name) if name is not None else default_name

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return super().available and self.data is not None
