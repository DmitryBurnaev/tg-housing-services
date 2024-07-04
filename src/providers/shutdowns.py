import datetime
from typing import NamedTuple

from src.config.app import SupportedService
from src.db.models import User, Address
from src.parsing.main import Parser


class ShutDownInfo(NamedTuple):
    start: datetime.datetime
    end: datetime.datetime
    address: str


class ShutDownProvider:
    @classmethod
    def for_address(cls, address: Address, service: SupportedService) -> list[ShutDownInfo]:
        service_data_parser = Parser(city=address.city)
        shutdowns = service_data_parser.parse(service, user_address=address)
        result: list[ShutDownInfo] = []
        for address, data_ranges in shutdowns.items():
            for data_range in data_ranges:
                result.append(
                    ShutDownInfo(start=data_range.start, end=data_range.end, address=address.raw)
                )

        return result
