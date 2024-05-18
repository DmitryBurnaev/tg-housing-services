import httpx
from lxml import html


def parse_website(url: str) -> list[tuple]:
    """
    Parses websites by URL's provided in params

    :param url: requested site which should be parsed
    """

    with httpx.Client() as client:
        response = client.get(url)

    tree = html.fromstring(response.content)
    rows = tree.xpath("//table/tr")
    data = []

    for row in rows:
        columns = row.xpath("td/text()")
        if len(columns) == 2:
            data.append((columns[0], columns[1]))

    return data
