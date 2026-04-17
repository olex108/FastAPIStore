# routers/product.py
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth import AuthUserService
from src.dependencies.permissions import PermissionChecker
from src.schemas.user import UserAuth
from src.config.database import db_handler
from src.crud.product import (
    create_product,
    delete_product_by_id,
    get_all_products,
    get_product_by_id,
    update_product_by_id,
)
from src.schemas.product import CreateProduct, Product, ProductOut

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", name="products", response_model=List[ProductOut])
async def get_products_list(
    current_user: Annotated[str, Depends(PermissionChecker(["products:view"]))],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    product_list = await get_all_products(session=session)
    return product_list


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
    print(product)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product '{product.name}' deleted"}
