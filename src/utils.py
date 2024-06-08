import re

ADDRESS_DEFAULT_PATTERN = re.compile(
    r"(?P<street_name>[\w\s.]+?),\s(?:д\.?|дом)\s*(?P<start_house>\d+)(?:[-–](?P<end_house>\d+))?(?:\sкорп\.\d+)?"
)


def get_street_and_house(address: str, pattern: re.Pattern[str] | None) -> tuple[str, list[int]]:
    """
    Searches street and house (or houses' range) from given string
    """
    if match := (pattern or ADDRESS_DEFAULT_PATTERN).search(address):
        street_name = match.group("street_name").strip()
        start_house = int(match.group("start_house"))
        end_house = int(match.group("end_house")) if match.group("end_house") else start_house
        houses = list(range(start_house, end_house + 1))
        return street_name, houses
    else:
        return "Unknown", []
