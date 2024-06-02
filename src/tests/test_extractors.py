import pytest

from src.parsing.checking import extract_street_and_house_info


@pytest.mark.parametrize(
    "address, expected_result",
    [
        (
            "Test Street пр., д.75 корп.1",
            {"street_name": "Test Street пр.", "houses": [75]},
        ),
        (
            "Test Street пр., д.75-79",
            {"street_name": "Test Street пр.", "houses": [75, 76, 77, 78, 79]},
        ),
        (
            "Test Street пр., д.79",
            {"street_name": "Test Street пр.", "houses": [79]},
        ),
        (
            "Test Street пр., дом 75",
            {"street_name": "Test Street пр.", "houses": [75]},
        ),
        (
            "Invalid Address Format",
            None,
        ),
    ],
)
def test_extract_street_and_house_info(address, expected_result):
    assert extract_street_and_house_info(address) == expected_result
