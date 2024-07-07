import datetime
from typing import NamedTuple

from src.config.app import SupportedService
from src.db.models import Address
from src.parsing.main import Parser


class ShutDownInfo(NamedTuple):
    start: datetime.datetime
    end: datetime.datetime
    address: str

    def __str__(self) -> str:
        return f"{self.address}: {self._dt_format(self.start)} - {self._dt_format(self.end)}"

    @staticmethod
    def _dt_format(dt: datetime.datetime) -> str:
        return dt.strftime("%d.%m.%Y %H:%M")


class ShutDownProvider:
    @classmethod
    def for_address(cls, address: str, service: SupportedService) -> list[ShutDownInfo]:
        user_address = Address.from_string(raw_address=address)
        service_data_parser = Parser(city=user_address.city)
        shutdowns = service_data_parser.parse(service, user_address=user_address)
        print(shutdowns)
        result: list[ShutDownInfo] = []
        for address, data_ranges in shutdowns.items():
            print(address, data_ranges)
            for data_range in data_ranges:
                result.append(
                    ShutDownInfo(start=data_range.start, end=data_range.end, address=address.raw)
                )

        return result
