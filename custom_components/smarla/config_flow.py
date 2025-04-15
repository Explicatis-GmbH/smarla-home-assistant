"""Config flow for Swing2Sleep Smarla integration."""

from __future__ import annotations

import logging

from pysmarlaapi import Connection
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_ACCESS_TOKEN

from .const import DOMAIN, HOST

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({CONF_ACCESS_TOKEN: str})


async def validate_input(data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        conn = Connection(url=HOST, token_b64=data[CONF_ACCESS_TOKEN])
    except ValueError:
        conn = None

    if conn is None:
        raise InvalidAuth

    _LOGGER.debug("Attempting authentication")

    token = await conn.get_token()

    if token is None:
        raise InvalidAuth

    return {"title": token.serialNumber, CONF_ACCESS_TOKEN: token.get_string()}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swing2Sleep Smarla."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}
        _LOGGER.debug("Validating input")

        try:
            info = await validate_input(user_input)
            return self.async_create_entry(
                title=info["title"],
                data={CONF_ACCESS_TOKEN: info.get(CONF_ACCESS_TOKEN)},
            )
        except InvalidAuth:
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
