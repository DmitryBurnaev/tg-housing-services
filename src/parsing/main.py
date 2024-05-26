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
            streets = row.xpath(".//td[@class='rowStreets']")[0].xpath(".//span/text()")
            print(streets)
            times = row.xpath("td/text()")[5:9]
            for street in streets:
                street: str = street.replace("\n", "").strip()
                result[street] = times
            # data.append((columns[0], columns[1]))

        return result

    @staticmethod
    def _get_street_and_house(address: str) -> tuple[str, int | None]:
        street, _, house = address.rpartition(" ")
        if str.isdigit(house):
            house = int(house)
        else:
            street, house = address, None

        logger.debug(f"Street: {street}, House: {house}")
        return street, house

    @staticmethod
    def _format_date(date: datetime) -> str:
        return date.date().strftime("%d.%m.%Y")
