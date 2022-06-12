from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from config.database import Base


class Restaurant(Base):
    __tablename__: str = "restaurant"

    id: Column = Column(Integer, primary_key=True, index=True, unique=True)
    city_id: Column = Column(Integer, ForeignKey("city.id"))
    city = relationship("City", back_populates="restaurants")
    name: Column = Column(String, nullable=False)
