from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class SeplosBMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Seplos BMS", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required('usb_port', default='/dev/ttyUSB0'): str,
            }),
            errors=errors,
            description_placeholders={
                'usb_port': 'e.g., /dev/ttyUSB0'
            }
        )
