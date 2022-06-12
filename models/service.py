from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from config.database import Base


class Service(Base):
    __tablename__: str = "service"

    id: Column = Column(Integer, primary_key=True, index=True, unique=True)
    name: Column = Column(String, nullable=False)
