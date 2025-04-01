"""Provides device actions for smarla devices."""

from __future__ import annotations

from pysmarlaapi import Federwiege
import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType, TemplateVarsType, VolDictType

from .const import DOMAIN
from .services import (
    ATTR_DEVICE,
    ATTR_INTENSITY,
    ATTR_INTENSITY_SCHEMA,
    DEVICE_SERVICES,
    SERVICE_SWING_START,
)

ACTION_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(DEVICE_SERVICES.keys()),
        vol.Optional(ATTR_INTENSITY): ATTR_INTENSITY_SCHEMA,
    }
)


def get_federwiege(hass: HomeAssistant, serial_number) -> Federwiege:
    """Get Federwiege object from serial_number."""
    federwiege_list: list[Federwiege] = hass.data[DOMAIN].values()
    for federwiege in federwiege_list:
        if federwiege.serial_number == serial_number:
            return federwiege
    return None


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: TemplateVarsType,
    context: Context | None,
) -> None:
    """Change state based on configuration."""
    data = {
        ATTR_DEVICE: config.get(CONF_DEVICE_ID),
    }
    if config[CONF_TYPE] == SERVICE_SWING_START and ATTR_INTENSITY in config:
        data[ATTR_INTENSITY] = config.get(ATTR_INTENSITY)
    await hass.services.async_call(
        DOMAIN, config[CONF_TYPE], data, blocking=True, context=context
    )


async def async_get_actions(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List device actions."""
    actions = []

    base_action = {
        CONF_DEVICE_ID: device_id,
        CONF_DOMAIN: DOMAIN,
    }

    for service in DEVICE_SERVICES:
        new_action = {**base_action, CONF_TYPE: service}
        actions.append(new_action)

    return actions


async def async_get_action_capabilities(
    hass: HomeAssistant, config: ConfigType
) -> dict[str, vol.Schema]:
    """List action capabilities."""
    if config[CONF_TYPE] != SERVICE_SWING_START:
        return {}

    extra_fields: VolDictType = {
        vol.Optional(ATTR_INTENSITY): ATTR_INTENSITY_SCHEMA,
    }

    return {"extra_fields": vol.Schema(extra_fields)}
