import re

ADDRESS_DEFAULT_PATTERN = re.compile(
    r"(?P<street_name>[\w\s.]+?),\s(?:д\.?|дом)\s*(?P<start_house>\d+)(?:[-–](?P<end_house>\d+))?(?:\sкорп\.\d+)?"
)


def get_street_and_house(
    address: str,
    pattern: re.Pattern[str] | None = None,
) -> tuple[str, list[int]]:
    """
    Searches street and house (or houses' range) from given string

    :param address: some string containing address with street and house (maybe range of houses)
    :param pattern: regexp's pattern for fetching street/houses from that
    :return <tuple> like ("My Street", [12]) or ("My Street", [12, 13, 14, 15])
    """
    if match := (pattern or ADDRESS_DEFAULT_PATTERN).search(address):
        street_name = match.group("street_name").strip()
        start_house = int(match.group("start_house"))
        end_house = int(match.group("end_house")) if match.group("end_house") else start_house
        houses = list(range(start_house, end_house + 1))
        return street_name, houses
    else:
        return "Unknown", []
