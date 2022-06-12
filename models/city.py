from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from config.database import Base


class City(Base):
    __tablename__: str = "city"

    id: Column = Column(Integer, primary_key=True, index=True, unique=True)
    name: Column = Column(String, nullable=False)
    # data: Column = Column(JSON, nullable=False)
    restaurants = relationship("Restaurant", back_populates="city")
