# from typing import List
#
# from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
# from sqlalchemy.orm import Mapped, mapped_column, relationship
#
# from .base import Base
# from .product import Product
#
#
# class Cart(Base):
#     __tablename__ = "carts"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), ondelete="CASCADE")
#
#     products: Mapped[List["Product"]] = relationship(
#         back_populates="products_list",
#         secondary="cart_products",
#     )
#
#
# class CartProducts(Base):
#     __tablename__ = "carts_products"
#
#     cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), primary_key=True)
#     product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
#     product_quantity: Mapped[int] = mapped_column()
