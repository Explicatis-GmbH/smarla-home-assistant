"""Support for the Swing2Sleep Smarla switch entities."""

from dataclasses import dataclass

from pysmarlaapi import Federwiege

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmarlaBaseEntity
from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class SmarlaSwitchEntityDescription(SwitchEntityDescription):
    """Class describing Swing2Sleep Smarla switch entities."""

    service: str
    property: str


NUMBER_TYPES: list[SmarlaSwitchEntityDescription] = [
    SmarlaSwitchEntityDescription(
        key="cradle",
        name=None,
        service="babywiege",
        property="swing_active",
    ),
    SmarlaSwitchEntityDescription(
        key="smartmode",
        translation_key="smartmode",
        service="babywiege",
        property="smartmode",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smarla switch from config entry."""
    federwiege = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[SmarlaSwitch] = []

    for desc in NUMBER_TYPES:
        entity = SmarlaSwitch(federwiege, desc)
        entities.append(entity)

    async_add_entities(entities)


class SmarlaSwitch(SmarlaBaseEntity, SwitchEntity):
    """Representation of Smarla switch."""

    async def on_change(self, value):
        """Notify ha when state changes."""
        self.async_write_ha_state()

    def __init__(
        self,
        federwiege: Federwiege,
        description: SmarlaSwitchEntityDescription,
    ) -> None:
        """Initialize an Smarla Switch."""
        super().__init__(federwiege)
        self.property = federwiege.get_service(description.service).get_property(
            description.property
        )
        self.entity_description = description
        self._attr_should_poll = False
        self._attr_unique_id = f"{federwiege.serial_number}-{description.key}"

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        await self.property.add_listener(self.on_change)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        await self.property.remove_listener(self.on_change)

    @property
    def is_on(self) -> bool:
        """Return the entity value to represent the entity state."""
        return self.property.get()

    async def async_turn_on(self) -> None:
        """Turn the switch on."""
        self.property.set(True)

    async def async_turn_off(self) -> None:
        """Turn the switch off."""
        self.property.set(False)
