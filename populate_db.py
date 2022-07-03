import asyncio

from config.database import SessionLocal, engine, Base
from models.city import City
from models.restaurant import Restaurant
from parsers import yandex_eda


Base.metadata.create_all(bind=engine)


async def main():
    db = SessionLocal()


    city_names: list[str] = ["Иркутск"]


    async with yandex_eda.Parser() as parser:
        data = {}

        cities: list[yandex_eda.City] = await parser.get_cities(city_names)



        tasks = []

        for city in cities:
            tasks.append(parser.get_restaurants(city))

            db.add(City(name=city.name))

        responses = await asyncio.gather(*tasks)





        restaurants: list[yandex_eda.Restaurant] = []
        for response in responses:
            restaurants.extend(response)

            # for restaurant in response:
            #     db.add(Restaurant(city=0, name=restaurant.name))

        db.commit()
        db.close()



        limit = asyncio.Semaphore(3)
        rate = 30.0

        tasks = [
            parser.get_products(restaurant, limit, rate)
            for restaurant in restaurants
        ]
    
        responses = await asyncio.gather(*tasks)


        products: list[yandex_eda.Product] = []

        for response in responses:
            products.extend(response)



        


if __name__ == "__main__":
    asyncio.run(main())
