"""The Swing2Sleep Smarla integration."""

import logging

from pysmarlaapi import Connection, Federwiege

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from .const import DOMAIN, HOST, PLATFORMS, STARTUP_MESSAGE
from .services import setup_services

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up this integration using YAML is not supported."""
    integration = await async_get_integration(hass, DOMAIN)
    _LOGGER.info(STARTUP_MESSAGE, integration.version)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    connection = Connection(HOST, token_str=entry.data.get(CONF_ACCESS_TOKEN, None))

    federwiege = Federwiege(hass.loop, connection)
    federwiege.register()
    federwiege.connect()

    hass.data[DOMAIN][entry.entry_id] = federwiege

    await hass.config_entries.async_forward_entry_setups(
        entry,
        list(PLATFORMS),
    )

    setup_services(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        list(PLATFORMS),
    )

    if unload_ok:
        hass.data[DOMAIN][entry.entry_id].disconnect()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.info("Reloading config entry: %s", entry)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class SmarlaBaseEntity(Entity):
    """Common Base Entity class for defining Smarla device."""

    def __init__(
        self,
        federwiege: Federwiege,
    ) -> None:
        """Initialise the entity."""
        super().__init__()

        self._attr_has_entity_name = True

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, federwiege.serial_number)},
            name="Federwiege",
            model="Smarla",
            manufacturer="Swing2Sleep",
            serial_number=federwiege.serial_number,
        )
