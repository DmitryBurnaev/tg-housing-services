import dataclasses
import datetime
import uuid
from typing import NamedTuple

from src.config.app import SupportedCity
from src.utils import get_street_and_house


class Address(NamedTuple):
    city: SupportedCity
    street: str
    house: int


class DateRange(NamedTuple):
    start: datetime.datetime
    end: datetime.datetime


@dataclasses.dataclass
class User:
    id: uuid.UUID
    name: str
    city: SupportedCity
    raw_address: str
    address: Address | None = None

    def __post_init__(self):
        street, houses = get_street_and_house(self.raw_address)
        house = houses[0] if houses else None
        self.address = Address(city=self.city, street=street, house=house)

    def send_notification(self, data: dict) -> None:
        print(f"hello, {self.name}! there is your update: {data}")
