import re


def extract_street_and_house_info(address):
    # Regular expression to match street name and house number with named groups
    street_regex = re.compile(
        r"(?P<street_name>[\w\s.]+?),\s(?:д\.?|дом)\s*(?P<start_house>\d+)(?:[-–](?P<end_house>\d+))?(?:\sкорп\.\d+)?"
    )
    match = street_regex.search(address)
    if match:
        street_name = match.group("street_name").strip()
        start_house = int(match.group("start_house"))
        end_house = int(match.group("end_house")) if match.group("end_house") else start_house

        # Generate house numbers in the range if any
        houses = list(range(start_house, end_house + 1))

        return {"street_name": street_name, "houses": houses}
    else:
        return None
