"""Support for the Swing2Sleep Smarla number entities."""

from dataclasses import dataclass

from pysmarlaapi import Federwiege

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmarlaBaseEntity
from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class SmarlaNumberEntityDescription(NumberEntityDescription):
    """Class describing Swing2Sleep Smarla number entities."""

    service: str
    property: str


NUMBER_TYPES: list[SmarlaNumberEntityDescription] = [
    SmarlaNumberEntityDescription(
        key="intensity",
        translation_key="intensity",
        service="babywiege",
        property="intensity",
        native_max_value=100,
        native_min_value=0,
        native_step=1,
        mode=NumberMode.SLIDER,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smarla number from config entry."""
    federwiege = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[SmarlaNumber] = []

    for desc in NUMBER_TYPES:
        entity = SmarlaNumber(federwiege, desc)
        entities.append(entity)

    async_add_entities(entities)


class SmarlaNumber(SmarlaBaseEntity, NumberEntity):
    """Representation of Smarla number."""

    async def on_change(self, value):
        """Notify ha when state changes."""
        self.async_write_ha_state()

    def __init__(
        self,
        federwiege: Federwiege,
        description: SmarlaNumberEntityDescription,
    ) -> None:
        """Initialize an Smarla number."""
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
    def native_value(self) -> float:
        """Return the entity value to represent the entity state."""
        return self.property.get()

    async def async_set_native_value(self, value: float) -> None:
        """Update to the vehicle."""
        self.property.set(int(value))
