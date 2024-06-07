import dataclasses
import uuid


@dataclasses.dataclass
class User:
    id: uuid.UUID
    name: str
    address_street: str
    address_house: int

    def send_notification(self, data: dict) -> None:
        print(f"hello, {self.name}! there is your update: {data}")
