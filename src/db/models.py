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
    raw: str

    def __eq__(self, other: "Address") -> bool:
        # TODO: replace with regular expression
        street = self.street.replace("пр.", "").replace("ул.", "").strip()
        other_street = other.street.strip()
        return self.city == other.city and street == other_street and self.house == other.house


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
        self.address = Address(city=self.city, street=street, house=house, raw=self.raw_address)

    def send_notification(self, date_ranges: dict[Address, set[DateRange]]) -> None:
        print(f"hello, {self.name}! Your Address: {self.address} | your dates: {date_ranges}")
