import pprint
import re
import hashlib
import logging
import urllib.parse
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

    def parse(self, service) -> dict[str, Any]:
        logger.debug(f"Parsing for service: {service} ({self.address})")
        return self._parse_website(service)

    def _get_content(self, service: SupportedService) -> str:
        url = self.urls[service].format(
            city=urllib.parse.quote_plus(CITY_NAME_MAP[self.city]),
            street=urllib.parse.quote_plus(self.street),
            date_start=self._format_date(datetime.now()),
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

        result = {}
        for row in rows:
            if row_streets := row.xpath(".//td[@class='rowStreets']"):
                streets = row_streets[0].xpath(".//span/text()")
                times = row.xpath("td/text()")[5:9]
                date_start, time_start, date_end, time_end = times
                for street in streets:
                    street_name, house = self._get_street_and_house(street.replace("\n", "").strip())
                    result[street_name] = {
                        "start": self._prepare_time(date_start, time_start),
                        "end": self._prepare_time(date_end, time_end),
                    }
        pprint.pprint(result, indent=4)
        return result

    @staticmethod
    def _get_street_and_house(address: str) -> tuple[str, list[int]]:
        return extract_street_and_house_numbers(address)
        # street, _, house = address.rpartition(" ")
        # print(f"{address=} {street=} {house=}")
        # if not (houses := parse_range_string(house)):
        #     street, houses = address, []
        #
        # logger.debug(f"Street: {street}, House: {houses}")
        # return street, houses

    @staticmethod
    def _format_date(date: datetime) -> str:
        return date.date().strftime("%d.%m.%Y")

    def _prepare_time(self, date: str, time: str) -> datetime:
        dt_string = f"{self._clear_string(date)}T{self._clear_string(time)}"
        return datetime.strptime(dt_string, f"%d-%m-%YT%H:%M")

    @staticmethod
    def _clear_string(src_string: str) -> str:
        return src_string.replace("\n", "").strip()


def parse_range_string(range_string):
    # Use regular expression to extract the numeric range or single number
    if range_string.isdigit():
        return [int(range_string.strip())]

    if match_range := re.search(r'(\d+)-(\d+)', range_string):
        start = int(match_range.group(1))
        end = int(match_range.group(2))
        return list(range(start, end + 1))

    if match_single := re.search(r'(\d+)', range_string):
        number = int(match_single.group(1))
        return [number]

    return []


def extract_street_and_house_numbers(address: str) -> tuple[str | None, list[int] | None]:
    """
    Define the regex pattern to find the street name, single house number, or a range using
    named groups
    """
    pattern = r"(?P<street>.+?),\s*д\.(?P<start>\d+)(?:-(?P<end>\d+))?"
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


# Example usage
addresses = [
    "Test пр., д.75",
    "Test пр., д.75-105"
]

for address in addresses:
    house_numbers = extract_house_numbers(address)
    if house_numbers:
        print(f"House numbers for '{address}': {house_numbers}")
    else:
        print(f"No house numbers found for '{address}'")



#
# # Example usage
# range_string_1 = "д56-60"
# parsed_array_1 = parse_range_string(range_string_1)
# print(parsed_array_1)  # Output: [56, 57, 58, 59, 60]
#
# range_string_2 = "д77"
# parsed_array_2 = parse_range_string(range_string_2)
# print(parsed_array_2)  # Output: [77]
