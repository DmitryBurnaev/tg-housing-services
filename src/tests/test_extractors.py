import pytest

from src.utils import get_street_and_house


@pytest.mark.parametrize(
    "address, expected_result",
    [
        (
            "Avenue Name пр., д.75 корп.1",
            {"street": "Avenue Name пр.", "houses": [75]},
        ),
        (
            "пр. Avenue Name         , д.75 корп.1",
            {"street": "Avenue Name", "houses": [75]},
        ),
        (
            "ул. Street Name, д.75",
            {"street": "Street Name", "houses": [75]},
        ),
        (
            "тракт Street Name, д.75",
            {"street": "Street Name", "houses": [75]},
        ),
        (
            "Avenue Name пр., д.75-79",
            {"street": "Avenue Name пр.", "houses": [75, 76, 77, 78, 79]},
        ),
        (
            "Avenue Name пр., д.79",
            {"street": "Avenue Name пр.", "houses": [79]},
        ),
        (
            "Avenue Name пр., дом 75",
            {"street": "Avenue Name пр.", "houses": [75]},
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
