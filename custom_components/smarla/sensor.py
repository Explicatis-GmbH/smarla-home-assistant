"""Support for the Swing2Sleep Smarla sensor entities."""

from dataclasses import dataclass

from pysmarlaapi import Federwiege

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmarlaBaseEntity
from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class SmarlaSensorEntityDescription(SensorEntityDescription):
    """Class describing Swing2Sleep Smarla number entities."""

    service: str
    property: str
    multiple: bool = False
    value_pos: int = 0


NUMBER_TYPES: list[SmarlaSensorEntityDescription] = [
    SmarlaSensorEntityDescription(
        key="amplitude",
        translation_key="amplitude",
        service="analyser",
        property="oscillation",
        multiple=True,
        value_pos=0,
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SmarlaSensorEntityDescription(
        key="period",
        translation_key="period",
        service="analyser",
        property="oscillation",
        multiple=True,
        value_pos=1,
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SmarlaSensorEntityDescription(
        key="activity",
        translation_key="activity",
        service="analyser",
        property="activity",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SmarlaSensorEntityDescription(
        key="swing_count",
        translation_key="swing_count",
        service="analyser",
        property="swing_count",
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smarla number from config entry."""
    federwiege = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[SmarlaSensor] = []

    for desc in NUMBER_TYPES:
        entity = SmarlaSensor(federwiege, desc)
        entities.append(entity)

    async_add_entities(entities)


class SmarlaSensor(SmarlaBaseEntity, SensorEntity):
    """Representation of Smarla sensor."""

    async def on_change(self, value):
        """Notify ha when state changes."""
        self.async_write_ha_state()

    def __init__(
        self,
        federwiege: Federwiege,
        description: SmarlaSensorEntityDescription,
    ) -> None:
        """Initialize an Smarla number."""
        super().__init__(federwiege)
        self.property = federwiege.get_service(description.service).get_property(
            description.property
        )
        self.entity_description = description
        self.multiple = description.multiple
        self.pos = description.value_pos
        self._attr_should_poll = False
        self._attr_unique_id = f"{federwiege.serial_number}-{description.key}"

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        await self.property.add_listener(self.on_change)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        await self.property.remove_listener(self.on_change)

    @property
    def native_value(self) -> int:
        """Return the entity value to represent the entity state."""
        return (
            self.property.get() if not self.multiple else self.property.get()[self.pos]
        )
