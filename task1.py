from operator import delitem
import requests
import json
import time

from typing import Any
from bs4 import BeautifulSoup
from decimal import Decimal

from parsers import delivery_club




def main() -> None:
    city_names: list[str] = ["Иркутск", "Омск"]

    parser: delivery_club.Parser = delivery_club.Parser()
    cities: list[delivery_club.City] = parser.get_cities(city_names)

    restaurants: list[delivery_club.Restaurant] = []

    for city in cities:
        restaurants.extend(parser.get_restaurants(city))

    print(f"Cities: {cities}")
    print(f"Restaurants: {restaurants}")



if __name__ == "__main__":
    main()
