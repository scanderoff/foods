from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from config.database import Base


class City(Base):
    __tablename__ = "city"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, nullable=False)
    restaurants = relationship("Restaurant", back_populates="city")
