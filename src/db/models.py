import dataclasses
import uuid
from typing import NamedTuple


class Address(NamedTuple):
    city: str
    street: str
    house: int


@dataclasses.dataclass
class User:
    id: uuid.UUID
    name: str
    raw_address: str
    address: Address | None = None

    def __post_init__(self):
        # TODO: use get_street_and_house instead
        street, house = self.raw_address.split(",")
        house = int(house.strip("д"))
        self.address = Address(street=street, house=house)

    def send_notification(self, data: dict) -> None:
        print(f"hello, {self.name}! there is your update: {data}")
