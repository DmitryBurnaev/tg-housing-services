import logging
import urllib.parse
from typing import Any
from datetime import datetime, timezone, timedelta

import httpx
from lxml import html

from src.config.app import RESOURCE_URLS, SupportedCity, SupportedService, CITY_NAME_MAP

logger = logging.getLogger(__name__)


class Parser:

    def __init__(self, city: SupportedCity, address: str) -> None:
        self.address = address
        self.street, self.house = self._get_street_and_house(address)
        self.urls = RESOURCE_URLS[city]
        self.city = city
        self.finish_date = (datetime.now(timezone.utc) + timedelta(days=30)).date()

    def parse(self, service) -> dict[str, Any]:
        logger.debug(f"Parsing for service: {service} ({self.address})")
        return self._parse_website(service)

    def _get_content(self, service: SupportedService) -> str:
        city_name = urllib.parse.quote_plus(CITY_NAME_MAP[self.city])
        url = self.urls[service].format(city=city_name, date_finish=self.finish_date.isoformat())
        logger.debug("Getting content for service: %s ...", url)
        with httpx.Client() as client:
            response = client.get(url)

        return response.text

    def _parse_website(self, service: SupportedService) -> dict[str, Any] | None:
        """
        Parses websites by URL's provided in params

        :param service: provide site's address which should be parsed
        :return: given data from website
        """

        html_content = self._get_content(service)

        tree = html.fromstring(html_content)
        rows = tree.xpath("//table/tr")
        data = []
        if not rows:
            logger.info("No data found for service: %s", service)
            return None

        for row in rows:
            columns = row.xpath("td/text()")
            if len(columns) == 2:
                data.append((columns[0], columns[1]))

        return dict(data)

    @staticmethod
    def _get_street_and_house(address: str) -> tuple[str, int | None]:
        street, _, house = address.rpartition(" ")
        if str.isdigit(house):
            house = int(house)
        else:
            street, house = address, None

        return street, house
