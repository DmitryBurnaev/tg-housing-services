import argparse
import logging.config
import uuid

from src.config.app import SupportedService, SupportedCity
from src.config.logging import LOGGING_CONFIG
from src.db.models import User
from src.parsing.main import Parser

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Process some addresses.")
    parser.add_argument("address", metavar="address", type=str)
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.captureWarnings(capture=True)

    args = parser.parse_args()
    parser = Parser(city=SupportedCity.SPB, address=args.address)

    user = User(
        id=uuid.uuid4(),
        name="TestUser",
        address_street="TestStreet",
        address_house=45
    )
    for service in SupportedService.__members__:
        result = parser.parse(service)
        logger.info(f"Parse Result: \n{result}")
        user.send_notification(result)


if __name__ == "__main__":
    main()
