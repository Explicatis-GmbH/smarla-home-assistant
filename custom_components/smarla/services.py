"""Swing2Sleep Smarla services."""

from __future__ import annotations

from pysmarlaapi import Federwiege
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import DOMAIN

ATTR_DEVICE = "device"
ATTR_INTENSITY = "intensity"

ATTR_INTENSITY_SCHEMA = vol.All(vol.Coerce(int), vol.Range(min=0, max=100))

SERVICE_SWING_START = "swing_start"
SERVICE_SWING_STOP = "swing_stop"

SERVICE_SWING_INCREASE = "swing_increase"
SERVICE_SWING_DECREASE = "swing_decrease"

SERVICE_FEDERWIEGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE): cv.string,
    }
)

SERVICE_SWING_START_SCHEMA = SERVICE_FEDERWIEGE_SCHEMA.extend(
    {
        vol.Optional(ATTR_INTENSITY): ATTR_INTENSITY_SCHEMA,
    }
)

DEVICE_SERVICES = {
    SERVICE_SWING_START: SERVICE_SWING_START_SCHEMA,
    SERVICE_SWING_STOP: SERVICE_FEDERWIEGE_SCHEMA,
    SERVICE_SWING_INCREASE: SERVICE_FEDERWIEGE_SCHEMA,
    SERVICE_SWING_DECREASE: SERVICE_FEDERWIEGE_SCHEMA,
}


def setup_services(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> None:
    """Register smarla service actions."""
    federwiege: Federwiege = hass.data[DOMAIN][config_entry.entry_id]

    async def service_handle(service_call: ServiceCall) -> None:
        """Start/Stop oscillation."""
        device_registry = dr.async_get(hass)
        device_id = service_call.data[ATTR_DEVICE]
        device_entry = device_registry.async_get(device_id)
        if not device_entry or device_entry.model != "Smarla":
            return

        if device_entry.serial_number != federwiege.serial_number:
            return

        service = federwiege.get_service("babywiege")

        if service_call.service == SERVICE_SWING_START:
            intensity = service_call.data.get(ATTR_INTENSITY)
            if intensity:
                service.get_property("intensity").set(int(intensity))
            service.get_property("swing_active").set(True)
        elif service_call.service == SERVICE_SWING_STOP:
            service.get_property("swing_active").set(False)
            service = federwiege.get_service("babywiege")
        elif service_call.service == SERVICE_SWING_INCREASE:
            intensity_prop = service.get_property("intensity")
            intensity_prop.set(intensity_prop.get() + 10)
        elif service_call.service == SERVICE_SWING_DECREASE:
            intensity_prop = service.get_property("intensity")
            intensity_prop.set(intensity_prop.get() - 10)

    for service, schema in DEVICE_SERVICES.items():
        hass.services.async_register(
            DOMAIN,
            service,
            service_handle,
            schema=schema,
        )
