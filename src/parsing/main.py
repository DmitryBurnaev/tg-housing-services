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
    address_regex = re.compile(
        r"(?P<street_name>[\w\s.]+?),\s(?:д\.?|дом)\s*(?P<start_house>\d+)(?:[-–](?P<end_house>\d+))?(?:\sкорп\.\d+)?"
    )

    def __init__(self, city: SupportedCity, address: str) -> None:
        self.address = address
        self.street, self.house = self.get_street_and_house(address)
        self.urls = RESOURCE_URLS[city]
        self.city = city
        self.finish_time_filter = datetime.now(timezone.utc) + timedelta(days=30)
        self.date_start = datetime.fromisoformat("2024-05-30")

    def parse(self, service: SupportedService) -> dict[str, Any] | None:
        logger.debug(f"Parsing for service: {service} ({self.address})")
        parsed_data = self._parse_website(service)
        logger.debug("Parsed data %s | \n%s", service, parsed_data)
        if found_items := parsed_data.get(self.street):
            logger.info("Found items for requested address:%s | %s", self.address, found_items)
            return found_items

        return None

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

    def _parse_website(self, service: SupportedService) -> dict[str, list[dict]] | None:
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
                date_start, time_start, date_end, time_end = dates
                print(date_start, time_start, date_end, time_end)
                print("---")
                for street in streets:
                    street_name, houses = self.get_street_and_house(
                        street.replace("\n", "").strip()
                    )
                    result[street_name].append(
                        {
                            "houses": houses,
                            "start": self._prepare_time(date_start, time_start),
                            "end": self._prepare_time(date_end, time_end),
                        }
                    )

        pprint.pprint(result, indent=4)
        return result

    @classmethod
    def get_street_and_house(cls, address: str) -> tuple[str, list[int]]:
        match = cls.address_regex.search(address)
        if match:
            street_name = match.group("street_name").strip()
            start_house = int(match.group("start_house"))
            end_house = int(match.group("end_house")) if match.group("end_house") else start_house
            houses = list(range(start_house, end_house + 1))
            return street_name, houses
        else:
            return "Unknown", []

    @staticmethod
    def _format_date(date: datetime) -> str:
        return date.date().strftime("%d.%m.%Y")

    def _prepare_time(self, date: str, time: str) -> datetime | None:
        date = self._clear_string(date)
        time = self._clear_string(time)
        if not (date and time):
            logger.warning("Missing date or time: date='%s' | time='%s'", date, time)
            return None

        try:
            result = datetime.strptime(f"{date}T{time}", "%d-%m-%YT%H:%M")
        except ValueError:
            logger.warning("Incorrect date / time: date='%s' | time='%s'", date, time)
            return None

        return result

    @staticmethod
    def _clear_string(src_string: str) -> str:
        return src_string.replace("\n", "").strip()
