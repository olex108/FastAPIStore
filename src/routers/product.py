# routers/product.py
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.permissions import PermissionChecker
from src.config.database import db_handler
from src.crud.product import (
    create_product,
    delete_product_by_id,
    get_all_products,
    get_product_by_id,
    update_product_by_id,
)
from src.schemas.product import CreateProduct, ProductOut, ProductPaginationOut
from src.config.settings import get_settings
from sqlalchemy import select
from src.models.product import Product




router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", name="products", response_model=List[ProductOut])
async def get_products_paginated_list(
    limit: Annotated[int, Query(**get_settings().pagination.model_dump())],
    cursor: Annotated[Optional[str], Query(None, description="price_id")],
    # sort_by: Annotated[str, Query("price_asc", regex="^(price_asc|price_desc|name_asc)$")],
    # name_query: Annotated[Optional[str], None],
    # current_user: Annotated[str, Depends(PermissionChecker(["products:view"]))],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):

    query = select(Product).order_by(Product.id).limit(limit)

    if cursor is not None:
        prod_price, prod_id = cursor.split("_")
        query.where(Product.id>prod_id)

    prod_list = await session.execute(query)
    prod_list = prod_list.scalars().all()


    product_list = await get_all_products(session=session)
    return product_list


# @router.get("/", name="products", response_model=List[ProductOut])
# async def get_products_list(
#     current_user: Annotated[str, Depends(PermissionChecker(["products:view"]))],
#     session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
# ):
#
#     product_list = await get_all_products(session=session)
#     return product_list


@router.get("/{product_id}", name="product", response_model=ProductOut)
async def get_product(
    product_id: int,
    current_user: Annotated[str, Depends(PermissionChecker(["products:view"]))],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):

    product = await get_product_by_id(product_id=product_id, session=session)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut)
async def create_new_product(
        product: CreateProduct,
        current_user: Annotated[str, Depends(PermissionChecker(["products:create"]))],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    new_product = await create_product(new_product=product, session=session)
    return new_product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product: CreateProduct,
    product_id: int,
    current_user: Annotated[str, Depends(PermissionChecker(["products:update"]))],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):

    updated_product = await update_product_by_id(product=product, product_id=product_id, session=session)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/{product_id}")
async def delete_product(
        product_id: int,
        current_user: Annotated[str, Depends(PermissionChecker(["products:delete"]))],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):

    product = await delete_product_by_id(product_id=product_id, session=session)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product '{product.name}' deleted"}
