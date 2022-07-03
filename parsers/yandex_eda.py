import json
import asyncio
import aiohttp
import logging

from typing import Any, NamedTuple
from bs4 import BeautifulSoup
from decimal import Decimal


# настройка логирования
LOGGER_FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(format=LOGGER_FORMAT, datefmt="[%H:%M:%S]")
log = logging.getLogger()
log.setLevel(logging.INFO)


# Храним всю необходимую инфу в таких контейнерах для удобства

class City(NamedTuple):
    id: int
    name: str


class Restaurant(NamedTuple):
    name: str
    slug: str


class Product(NamedTuple):
    name: str
    description: str
    # calories: int
    # weight: int
    price: Decimal
    image: str
    

class Parser:
    BASE_URL: str = "https://eda.yandex.ru"


    def __init__(self) -> None:
        # одна сессия на все запросы
        # закрываем при выходе из контекстного менеджера
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo) -> None:
        await self.session.close()

    async def get_cities(self, city_names: list[str] = []) -> list[City]:
        server_data = await self.__get_server_data(Parser.BASE_URL)
        city_items = server_data["regionsData"]

        if city_names:
            city_items = filter(lambda ci: ci["name"] in city_names, city_items)

        cities: list[City] = []
        
        for city_item in city_items:
            city = City(city_item["id"], city_item["name"])

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
                    restaurant = Restaurant(
                        place["name"],
                        place["slug"],
                    )

                    restaurants.append(restaurant)

            return restaurants
    
    async def get_products(
        self,
        restaurant: Restaurant,
        limit: asyncio.Semaphore,
        rate: float
    ) -> list[Product]:
        """
        Парсинг продуктов.
        Нужен слаг ресторана и всё получаем одним GET запросом
        limit - количество запросов за раз
        rate - задержка перед следующим пакетом limit запросов
        """

        async with limit, self.session.get(f"{Parser.BASE_URL}/api/v2/catalog/{restaurant.slug}/menu", headers={
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        }, ssl=False) as response:

            log.info("PRODUCT REQUEST")

            data = await response.json()
            categories = data["payload"]["categories"]

            products: list[Product] = []

            for category in categories:
                if not category["id"]:
                    continue

                items = category["items"]

                for item in items:
                    picture = item.get("picture")
                    image = ""

                    if picture is not None:
                        image = item["picture"]["uri"]
                        image = image.replace("{w}", "450").replace("{h}", "300")

                    product = Product(
                        item["name"],
                        item.get("description", ""),
                        Decimal(item["price"]),
                        image,
                    )

                    products.append(product)

            # if limit.locked():
                # print("Concurrency limit reached, waiting ...")
            await asyncio.sleep(rate)

            return products

    async def __get_server_data(self, url: str) -> dict[str, Any]:
        """
        На страницах Yandex Eda есть скрытый объект со множество полезной инфы
        Метод возвращает этот объект
        """

        async with self.session.get(url, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        }, ssl=False) as response:

            text = await response.text()
            soup = BeautifulSoup(text, features="html.parser")
            body = soup.find("body")
            scripts = body.find_all("script")

            server_data: str = scripts[2].text[18:].rstrip(";")

            return json.loads(server_data)
