import datetime
from typing import NamedTuple

from src.config.app import SupportedService
from src.db.models import Address
from src.parsing.main import Parser


class ShutDownInfo(NamedTuple):
    start: datetime.datetime
    end: datetime.datetime
    address: str


class ShutDownProvider:
    @classmethod
    def for_address(cls, address: str, service: SupportedService) -> list[ShutDownInfo]:
        user_address = Address.from_string(raw_address=address)
        service_data_parser = Parser(city=user_address.city)
        shutdowns = service_data_parser.parse(service, user_address=user_address)
        result: list[ShutDownInfo] = []
        for address, data_ranges in shutdowns.items():
            for data_range in data_ranges:
                result.append(
                    ShutDownInfo(start=data_range.start, end=data_range.end, address=address.raw)
                )

        return result
