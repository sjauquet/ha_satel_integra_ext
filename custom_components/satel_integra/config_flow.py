"""Config flow for Satel Integra integration."""
from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

from satel_integra2.satel_integra import AsyncSatel

from .const import (
    _LOGGER,
    CONF_DEVICE_CODE,
    CONF_MODULE_TYPE,
    DEFAULT_PORT,
    DOMAIN,
    MODULE_ETHM1,
    MODULE_ETHM1_PLUS,
)

_STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MODULE_TYPE, default=MODULE_ETHM1_PLUS): selector(
            {
                "select": {
                    "options": [
                        {"value": MODULE_ETHM1_PLUS, "label": "ETHM-1 Plus"},
                        {"value": MODULE_ETHM1, "label": "ETHM-1"},
                    ]
                }
            }
        ),
        vol.Required(CONF_HOST): selector({"text": {}}),
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): selector(
            {"number": {"min": 1, "max": 65535, "mode": "box"}}
        ),
        vol.Optional(CONF_DEVICE_CODE): selector({"text": {"type": "password"}}),
    }
)


class SatelIntegraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Satel Integra."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return SatelIntegraOptionsFlow()

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            polling_mode = user_input.get(CONF_MODULE_TYPE) == MODULE_ETHM1

            try:
                controller = AsyncSatel(
                    host,
                    port,
                    asyncio.get_event_loop(),
                    polling_mode=polling_mode,
                )
                connected = await controller.connect()
                controller.close()

                if not connected:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Satel Integra ({host})",
                        data=user_input,
                    )
            except Exception:
                _LOGGER.exception("Unexpected error during connection test")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=_STEP_USER_SCHEMA,
            errors=errors,
        )


class SatelIntegraOptionsFlow(config_entries.OptionsFlow):
    """Options flow — re-scan devices."""

    async def async_step_init(self, user_input=None):
        """Show re-scan confirmation and trigger it on submit."""
        if user_input is not None:
            # Clear the discovery cache from entry.data
            new_data = {
                k: v for k, v in self.config_entry.data.items()
                if k not in ("discovered_zones", "discovered_partitions", "discovered_outputs")
            }
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            _LOGGER.info("Discovery cache cleared — reloading integration for re-scan")
            # Schedule reload after the options flow completes
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self.config_entry.entry_id)
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        )
