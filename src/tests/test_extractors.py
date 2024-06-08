import pytest

from src.utils import get_street_and_house


@pytest.mark.parametrize(
    "address, expected_result",
    [
        (
            "Test Street пр., д.75 корп.1",
            {"street": "Test Street пр.", "houses": [75]},
        ),
        (
            "Test Street пр., д.75-79",
            {"street": "Test Street пр.", "houses": [75, 76, 77, 78, 79]},
        ),
        (
            "Test Street пр., д.79",
            {"street": "Test Street пр.", "houses": [79]},
        ),
        (
            "Test Street пр., дом 75",
            {"street": "Test Street пр.", "houses": [75]},
        ),
        (
            "Invalid Address Format",
            {"houses": [], "street": "Unknown"},
        ),
    ],
)
def test_extract_street_and_house_info(address, expected_result):
    street, houses = get_street_and_house(address)
    assert {"street": street, "houses": houses} == expected_result
