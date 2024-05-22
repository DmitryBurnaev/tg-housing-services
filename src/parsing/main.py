from typing import Any

import httpx
from lxml import html

from src.config.app import RESOURCE_URLS, SupportedCity, SupportedService, CITY_NAME_MAP


class Parser:

    def __init__(self, city: SupportedCity, address: str) -> None:
        self.address = address
        self.urls = RESOURCE_URLS[city]
        self.city = city

    def parse(self, service) -> dict[str, Any]:
        print(f"Parsing for service: {service} ({self.address})")
        return self._parse_website(service)

    def _get_content(self, service: SupportedService) -> str:
        city_name = CITY_NAME_MAP[self.city]
        url = self.urls[service].format(city=city_name, date_finish="18.06.2024")
        with httpx.Client() as client:
            response = client.get(url)

        return response.text

    def _parse_website(self, service: SupportedService) -> dict[str, Any]:
        """
        Parses websites by URL's provided in params

        :param service: provide site's address which should be parsed
        :return: given data from website
        """

        html_content = self._get_content(service)

        tree = html.fromstring(html_content)
        rows = tree.xpath("//table/tr")
        data = []

        for row in rows:
            columns = row.xpath("td/text()")
            if len(columns) == 2:
                data.append((columns[0], columns[1]))

        return dict(data)
