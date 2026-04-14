from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.product import Product, CreateProduct, ProductOut
from src.config.database import db_handler
from src.crud.product import get_all_products, create_product, get_product_by_id, update_product_by_id, delete_product_by_id


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/", name="products", response_model=List[ProductOut])
async def get_products_list(session: AsyncSession = Depends(db_handler.session_getter)):
    product_list = await get_all_products(session=session)
    return product_list


@router.get("/{product_id}", name="product", response_model=ProductOut)
async def get_product(product_id: int, session: AsyncSession = Depends(db_handler.session_getter)):
    product = await get_product_by_id(product_id=product_id, session=session)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut)
async def create_new_product(product: CreateProduct, session: AsyncSession = Depends(db_handler.session_getter)):
    new_product = await create_product(new_product=product, session=session)
    return new_product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product: CreateProduct, product_id: int, session: AsyncSession = Depends(db_handler.session_getter)):
    updated_product = await update_product_by_id(product=product, product_id=product_id, session=session)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/{product_id}")
async def delete_product(product_id: int, session: AsyncSession = Depends(db_handler.session_getter)):
    product = await delete_product_by_id(product_id=product_id, session=session)
    print(product)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product '{product.name}' deleted"}
