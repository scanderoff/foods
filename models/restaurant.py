from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from config.database import Base


class Restaurant(Base):
    __tablename__ = "restaurant"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    city_id = Column(Integer, ForeignKey("city.id"), nullable=False)
    city = relationship("City", back_populates="restaurants")
    name = Column(String, nullable=False)
