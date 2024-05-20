import argparse

from src.config.app import SupportedService, SupportedCity
from src.parsing.main import Parser


def main():
    parser = argparse.ArgumentParser(description="Process some addresses.")
    parser.add_argument('address', metavar='address', type=str)
    args = parser.parse_args()
    parser = Parser(city=SupportedCity.SPB, address=args.address)
    for service in SupportedService.__members__:
        result = parser.parse(service)
        print(f"Parse Result: \n{result}")


if __name__ == '__main__':
    main()
