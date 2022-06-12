import requests
import json
import aiohttp

from typing import Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
from decimal import Decimal


@dataclass
class City:
    id: int
    name: str


@dataclass
class Restaurant:
    name: str
    slug: str


@dataclass
class Product:
    name: str
    description: str
    # calories: int
    # weight: int
    price: Decimal
    image: str
    

class Parser:
    BASE_URL: str = "https://eda.yandex.ru"


    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.session.close()

    async def get_cities(self, city_names: list[str] = []) -> list[City]:
        server_data = await self._get_server_data(Parser.BASE_URL)
        city_items = server_data["regionsData"]

        if city_names:
            city_items = filter(lambda ci: ci["name"] in city_names, city_items)

        cities: list[City] = []
        
        for city_item in city_items:
            city: City = City(city_item["id"], city_item["name"])

            cities.append(city)

        return cities
    
    async def get_restaurants(self, city: City) -> list[Restaurant]:
        async with self.session.post(f"{Parser.BASE_URL}/eats/v1/layout-constructor/v1/layout", json={
            "filters": [],
            "region_id": city.id,
        }, headers={
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
            "X-Device-Id": "l474pvst-wykhlm88rul-5v14mmsxh5q-vvq93ekjjs",
        }, ssl=False) as response:

            data = await response.json()

            restaurants: list[Restaurant] = []

            places_lists = data["data"]["places_lists"]

            for place_list in places_lists:
                places = place_list["payload"]["places"]

                for place in places:
                    restaurant: Restaurant = Restaurant(
                        place["name"],
                        place["slug"],
                    )

                    restaurants.append(restaurant)

            return restaurants
    
    async def get_products(self, restaurant: Restaurant) -> list[Product]:
        async with self.session.get(f"{Parser.BASE_URL}/api/v2/catalog/{restaurant.slug}/menu", headers={
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        }, ssl=False) as response:

            data = await response.json()
            categories = data["payload"]["categories"]

            products: list[Product] = []

            for category in categories:
                if not category["id"]:
                    continue

                items = category["items"]

                for item in items:
                    picture = item.get("picture")
                    image: str = ""

                    if picture is not None:
                        image = item["picture"]["uri"]
                        image = image.replace("{w}", "450").replace("{h}", "300")

                    product: Product = Product(
                        item["name"],
                        item.get("description", ""),
                        Decimal(item["price"]),
                        image,
                    )

                    products.append(product)

            return products

    async def _get_server_data(self, url: str) -> dict[str, Any]:
        async with self.session.get(url, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        }, ssl=False) as response:

            soup = BeautifulSoup(await response.text(), features="html.parser")
            body = soup.find("body")
            scripts = body.find_all("script")

            server_data: str = scripts[2].text[18:].rstrip(";")

            return json.loads(server_data)
