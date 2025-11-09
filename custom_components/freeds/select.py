"""Platform for FreeDS Mode select integration."""
from __future__ import annotations
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.event import async_track_state_change_event
from .const import DOMAIN
from .entity import FreeDSEntity

MODE_OPTIONS = ["OFF", "MAN", "AUTO"]

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add FreeDS Mode select entity."""
    common_data = hass.data[DOMAIN][config_entry.data["uniqueid"]]
    async_add_entities([
        FreeDSModeSelect(
            hass=hass,
            name="Mode",
            icon="mdi:thermostat",
            #entity_category=EntityCategory.CONFIG,
            **common_data
        )
    ])

class FreeDSModeSelect(FreeDSEntity, SelectEntity):
    """FreeDS Mode select entity."""

    def __init__(self, hass: HomeAssistant, **kwargs):
        super().__init__(**kwargs)
        self.hass = hass
        self._attr_options = MODE_OPTIONS
        self._attr_current_option = "OFF"
        self._switch_1 = "switch.boiler_pwm_enabled"
        self._switch_2 = "switch.boiler_pwm_manual_mode"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        async_track_state_change_event(
            self.hass,
            [self._switch_1, self._switch_2],
            self._handle_switch_change
        )
        await self._update_mode_from_switches()

    @callback
    async def _handle_switch_change(self, event):
        await self._update_mode_from_switches()

    async def _update_mode_from_switches(self):
        s1 = self.hass.states.get(self._switch_1)
        s2 = self.hass.states.get(self._switch_2)
        if not s1 or not s2:
            return

        new_mode = "OFF" if s1.state != "on" else "MAN" if s2.state == "on" else "AUTO"
        if new_mode != self._attr_current_option:
            self._attr_current_option = new_mode
            self.async_write_ha_state()

    async def async_select_option(self, option: str):
        if option not in MODE_OPTIONS:
            return

        self._attr_current_option = option

        if option == "OFF":
            await self._set_switches(False, False)
        elif option == "MAN":
            await self._set_switches(True, True)
        else:  # AUTO
            await self._set_switches(True, False)

        self.async_write_ha_state()

    async def _set_switches(self, s1_on: bool, s2_on: bool):
        await self.hass.services.async_call(
            "switch", "turn_on" if s1_on else "turn_off",
            {"entity_id": self._switch_1}, blocking=True
        )
        await self.hass.services.async_call(
            "switch", "turn_on" if s2_on else "turn_off",
            {"entity_id": self._switch_2}, blocking=True
        )
