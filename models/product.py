from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from config.database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"))
    restaurant = relationship("Restaurant", back_populates="products")
    name = Column(String, nullable=False)
