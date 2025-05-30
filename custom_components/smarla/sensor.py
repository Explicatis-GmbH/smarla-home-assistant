"""Support for the Swing2Sleep Smarla sensor entities."""

from dataclasses import dataclass

from pysmarlaapi import Federwiege
from pysmarlaapi.federwiege.classes import Property

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FederwiegeConfigEntry
from .entity import SmarlaBaseEntity


@dataclass(frozen=True, kw_only=True)
class SmarlaSensorEntityDescription(SensorEntityDescription):
    """Class describing Swing2Sleep Smarla sensor entities."""

    service: str
    property: str
    multiple: bool = False
    value_pos: int = 0


SENSORS: list[SmarlaSensorEntityDescription] = [
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
    config_entry: FederwiegeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Smarla sensors from config entry."""
    federwiege = config_entry.runtime_data
    async_add_entities(SmarlaSensor(federwiege, desc) for desc in SENSORS)


class SmarlaSensor(SmarlaBaseEntity, SensorEntity):
    """Representation of Smarla sensor."""

    entity_description: SmarlaSensorEntityDescription

    _property: Property[int]

    def __init__(
        self,
        federwiege: Federwiege,
        desc: SmarlaSensorEntityDescription,
    ) -> None:
        """Initialize a Smarla sensor."""
        prop = federwiege.get_property(desc.service, desc.property)
        super().__init__(federwiege, prop)
        self.entity_description = desc
        self.multiple = desc.multiple
        self.pos = desc.value_pos
        self._attr_unique_id = f"{federwiege.serial_number}-{desc.key}"

    @property
    def native_value(self) -> int:
        """Return the entity value to represent the entity state."""
        value = self._property.get()
        return value if not self.multiple else value[self.pos]
