"""Support for the Brink Home API."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DATA_CLIENT,
    DATA_COORDINATOR,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PARAM_DEVICE_TYPE,
    PARAM_SOFTWARE_LABEL,
)
from .core.brink_home_cloud import BrinkAuthError, BrinkHomeCloud

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SELECT, Platform.BINARY_SENSOR, Platform.SENSOR, Platform.FAN, Platform.NUMBER]

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=False)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Brink Home from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    scan_interval = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    session = async_get_clientsession(hass)
    brink_client = BrinkHomeCloud(session, username, password)

    try:
        await brink_client.login()
    except BrinkAuthError as ex:
        await brink_client.close()
        raise ConfigEntryAuthFailed from ex
    except aiohttp.ClientResponseError as ex:
        await brink_client.close()
        if ex.status == 401:
            raise ConfigEntryAuthFailed from ex
        raise ConfigEntryNotReady from ex
    except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
        await brink_client.close()
        raise ConfigEntryNotReady from ex

    async def async_update_data() -> dict[int, dict[str, Any]]:
        try:
            return await async_get_devices(brink_client)
        except BrinkAuthError as ex:
            raise ConfigEntryAuthFailed from ex
        except aiohttp.ClientResponseError as ex:
            if ex.status == 401:
                raise ConfigEntryAuthFailed from ex
            raise UpdateFailed(ex) from ex
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            raise UpdateFailed(ex) from ex

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        config_entry=entry,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_CLIENT: brink_client,
        DATA_COORDINATOR: coordinator,
    }

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await brink_client.close()
        raise

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_get_devices(brink_client: BrinkHomeCloud) -> dict[int, dict[str, Any]]:
    """Fetch and normalize Brink systems plus the parameters this integration uses."""
    systems = await brink_client.get_systems()

    _LOGGER.debug("Brink Flair systems: %s", systems)

    # device = await brink_client.get_device(3074)

    # _LOGGER.debug("Brink Flair device: %s", device)

    # gateway_type_id = device.get("gatewayTypeId")
    # is_online = device.get("isOnline")

    # _LOGGER.debug("Brink Flair gateway_type_id: %s", gateway_type_id) # always 3 ?
    # _LOGGER.debug("Brink Flair device is_online: %s", is_online)

    devices: dict[int, dict[str, Any]] = {}
    for system in systems:
        system_id = system["system_id"]
        device = await brink_client.get_device(system_id)
        _LOGGER.debug("Brink Flair device: %s", device)
        gateway_type_id = device.get("gatewayTypeId")
        is_online = device.get("isOnline")
        parameters = await brink_client.get_device_data(system_id)
        _LOGGER.debug("Brink Flair device parameters: %s", parameters)
        devices[system_id] = {
            "system_id": system_id,
            "name": system.get("name") or DEFAULT_NAME,
            "serial_number": system.get("serial_number"),
            "gateway_state": system.get("gateway_state"),
            "gateway_type_id": gateway_type_id,
            "device_is_online": is_online,
            "model": parameters.get(PARAM_DEVICE_TYPE, {}).get("value") or DEFAULT_MODEL,
            "sw_version": parameters.get(PARAM_SOFTWARE_LABEL, {}).get("value"),
            "parameters": parameters,
        }

    return devices


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        runtime = hass.data[DOMAIN].pop(entry.entry_id)
        await runtime[DATA_CLIENT].close()
    return unload_ok
