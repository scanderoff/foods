import asyncio

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
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def populate_db():
    db = SessionLocal()
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
    




    return templates.TemplateResponse("products.html", {
        "request": request,

        # "products": products,
    })
