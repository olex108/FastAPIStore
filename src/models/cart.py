from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .product import Product

class Cart(Base):
    pass
#     __tablename__ = 'carts'
#     id = Column(Integer, primary_key=True)
#     products = Column(M)
