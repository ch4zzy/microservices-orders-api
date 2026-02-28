from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Order(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    quantity = Column(Integer)
