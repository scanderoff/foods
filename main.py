import asyncio

from typing import Any
import aiohttp

from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config.database import SessionLocal, engine, Base

from models.city import City
from models.restaurant import Restaurant
# from models.product import Product
from parsers import yandex_eda


app = FastAPI()
templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)


def get_db():
    db: SessionLocal = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def populate_db():
    db: SessionLocal = SessionLocal()
    num_cities = db.query(City).count()

    if num_cities == 0:
        cities: list[str] = ["Москва", "Санкт-Петербург", "Иркутск", "Самара"]

        for city_name in cities:
            db.add(City(name=city_name))
        
        db.commit()
    else:
        print(f"{num_cities} cities already in DB")
    
    db.close()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)) -> Response:
    # async with aiohttp.ClientSession() as session:
    #     async with session.post("https://eda.yandex.ru/eats/v1/layout-constructor/v1/layout", json={
    #             "filters": [],
    #             "region_id": 110,
    #         }, headers={
    #             "Accept": "application/json, text/plain, */*",
    #             "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
    #             "X-Device-Id": "l474pvst-wykhlm88rul-5v14mmsxh5q-vvq93ekjjs",
    #         }, ssl=False) as response:

    #         print(await response.text())

    
    city_names: list[str] = ["Иркутск"]

    async with yandex_eda.Parser() as parser:
        cities: list[yandex_eda.City] = await parser.get_cities(city_names)

        print(cities)

        tasks = [parser.get_restaurants(city) for city in cities]
        responses = await asyncio.gather(*tasks)


        restaurants: list[yandex_eda.Restaurant] = []
        for response in responses:
            restaurants.extend(response)

        print(restaurants)
        print(f"Restaurants found: {len(restaurants)}")




        tasks = [parser.get_products(restaurant) for restaurant in restaurants]
        responses = await asyncio.gather(*tasks)


        products: list[yandex_eda.Product] = []
        # for response in responses:
        #     products.extend(response)
        products.extend(responses[0])

        print(f"Products found: {len(products)}")



    return templates.TemplateResponse("products.html", {
        "request": request,

        "products": products,
    })


@app.get("/test", response_class=HTMLResponse)
async def test(request: Request, db: Session = Depends(get_db)) -> Response:
    city_names: list[str] = ["Иркутск", "Омск"]



    # async with delivery_club.Parser() as parser:
    #     cities: list[delivery_club.City] = await parser.get_cities(city_names)


    #     tasks = [parser.get_restaurants(city) for city in cities]
    #     responses = await asyncio.gather(*tasks)


    #     restaurants: list[delivery_club.Restaurant] = []
    #     for response in responses:
    #         restaurants.extend(response)

    #     print(f"Restaurants found: {len(restaurants)}")



    #     tasks = [parser.get_products(restaurant) for restaurant in restaurants]
    #     responses = await asyncio.gather(*tasks)


    #     products: list[delivery_club.Product] = []
    #     for response in responses:
    #         products.extend(response)

    #     print(f"Products found: {len(products)}")




    return templates.TemplateResponse("restaurants.html", {
        "request": request,
    })


