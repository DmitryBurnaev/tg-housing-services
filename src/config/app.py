import enum
import os
from pathlib import Path


class SupportedCity(enum.StrEnum):
    SPB = "SPB"
    RND = "RND"


class SupportedService(enum.StrEnum):
    ELECTRICITY = "ELECTRICITY"
    COLD_WATER = "COLD_WATER"
    HOT_WATER = "HOT_WATER"


PROJECT_PATH = Path(__file__).parent.parent.absolute()
ROOT_PATH = PROJECT_PATH.parent
DATA_PATH = ROOT_PATH / ".data"
os.makedirs(DATA_PATH, exist_ok=True)

RESOURCE_URLS = {
    SupportedCity.SPB: {
        SupportedService.ELECTRICITY: "https://rosseti-lenenergo.ru/planned_work/?city={city}&date_start={date_start}&date_finish={date_finish}&street={street}",
        SupportedService.HOT_WATER: "https://www.gptek.spb.ru/grafik/",
        SupportedService.COLD_WATER: "https://www.vodokanal.spb.ru/presscentr/remontnye_raboty/",
    }
# https://rosseti-lenenergo.ru/planned_work/?reg=&city=%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3&date_start=26.05.2024&date_finish=26.06.2024&res=&street=%D0%9A%D0%BE%D0%BD%D0%B4%D1%80%D0%B0%D1%82%D1%8C%D0%B5%D0%B2%D1%81%D0%BA%D0%B8%D0%B9
# ex: https://www.gptek.spb.ru/grafik/?street=%D0%9A%D0%BE%D0%BC%D0%B5%D0%BD%D0%B4%D0%B0%D0%BD%D1%82%D1%81%D0%BA%D0%B8%D0%B9+%D0%BF%D1%80-%D0%BA%D1%82&house=18
# https://rosseti-lenenergo.ru/planned_work/?reg=&city=%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3&date_start=&date_finish=18.06.2024&res=&street=
# https://rosseti-lenenergo.ru/planned_work/?city=&date_start=&date_finish=18.06.2024&res=&street=%D1%83%D0%BB+%D0%9E%D0%BB%D0%B5%D0%BA%D0%BE+%D0%94%D1%83%D0%BD%D0%B4%D0%B8%D1%87%D0%B0
}

CITY_NAME_MAP = {
    SupportedCity.SPB: "Санкт-Петербург",
}

TG_BOT_API_KEY = os.getenv("TG_BOT_API_KEY")
TG_TEST_USERS_LIST = os.getenv("TG_TEST_USERS_LIST", "").split(",")
