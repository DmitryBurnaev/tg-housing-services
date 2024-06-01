import pprint
import re
import hashlib
import logging
import urllib.parse
from collections import defaultdict
from typing import Any
from datetime import datetime, timezone, timedelta

import httpx
from lxml import html

from src.config.app import RESOURCE_URLS, SupportedCity, SupportedService, CITY_NAME_MAP, DATA_PATH

logger = logging.getLogger(__name__)


class Parser:
    date_format = "%d.%m.%Y"

    def __init__(self, city: SupportedCity, address: str) -> None:
        self.address = address
        self.street, self.house = self._get_street_and_house(address)
        self.urls = RESOURCE_URLS[city]
        self.city = city
        self.finish_time_filter = datetime.now(timezone.utc) + timedelta(days=30)
        self.date_start = datetime.fromisoformat("2024-05-30")

    def parse(self, service) -> dict[str, Any]:
        logger.debug(f"Parsing for service: {service} ({self.address})")
        return self._parse_website(service)

    def _get_content(self, service: SupportedService) -> str:
        url = self.urls[service].format(
            city=urllib.parse.quote_plus(CITY_NAME_MAP[self.city]),
            street=urllib.parse.quote_plus(self.street.encode()) if self.street else "",
            date_start=self._format_date(self.date_start),
            date_finish=self._format_date(self.finish_time_filter),
        )
        tmp_file_path = (
            DATA_PATH / f"{service.lower()}_{hashlib.sha256(url.encode("utf-8")).hexdigest()}.html"
        )
        if tmp_file_path.exists():
            return tmp_file_path.read_text()

        logger.debug("Getting content for service: %s ...", url)
        with httpx.Client() as client:
            response = client.get(url)
            response_data = response.text

        tmp_file_path.touch()
        tmp_file_path.write_text(response_data)
        return response_data

    def _parse_website(self, service: SupportedService) -> dict[str, Any] | None:
        """
        Parses websites by URL's provided in params

        :param service: provide site's address which should be parsed
        :return: given data from website
        """

        html_content = self._get_content(service)
        tree = html.fromstring(html_content)
        rows = tree.xpath("//table/tbody/tr")
        if not rows:
            logger.info("No data found for service: %s", service)
            return None

        result = defaultdict(list)
        for row in rows:
            if row_streets := row.xpath(".//td[@class='rowStreets']"):
                streets = row_streets[0].xpath(".//span/text()")
                dates = row.xpath("td/text()")[5:9]
                print(dates)
                date_start, time_start, date_end, time_end = row.xpath("td/text()")[5:9]
                print(date_start, time_start, date_end, time_end)
                print("---")
                for street in streets:
                    street_name, houses = self._get_street_and_house(street.replace("\n", "").strip())
                    result[street_name].append(
                        {
                            "houses": houses,
                            "start": self._prepare_time(date_start, time_start),
                            "end": self._prepare_time(date_end, time_end),
                        }
                    )

        pprint.pprint(result, indent=4)
        return result

    @staticmethod
    def _get_street_and_house(address: str) -> tuple[str, list[int]]:
        return extract_street_and_house_numbers(address)

    @staticmethod
    def _format_date(date: datetime) -> str:
        return date.date().strftime("%d.%m.%Y")

    def _prepare_time(self, date: str, time: str) -> datetime | None:
        date = self._clear_string(date)
        time = self._clear_string(time)
        if date and time:
            return datetime.strptime(f"{date}T{time}", "%d-%m-%YT%H:%M")

        return None

    @staticmethod
    def _clear_string(src_string: str) -> str:
        return src_string.replace("\n", "").strip()


def extract_street_and_house_numbers(address: str) -> tuple[str | None, list[int] | None]:
    """
    Define the regex pattern to find the street name, single house number, or a range using
    named groups
    """
    pattern = r"(?P<street>.+?),?(?P<start>\d+)(?:-(?P<end>\d+))?"
    match = re.search(pattern, address)
    if match:
        street_name: str = match.group('street')
        start_number = int(match.group('start'))
        if match.group('end'):
            end_number = int(match.group('end'))
            house_numbers: list[int] = list(range(start_number, end_number + 1))
        else:
            house_numbers: list[int] = [start_number]
        return street_name, house_numbers

    return None, None
