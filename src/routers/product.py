# routers/product.py
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.pagination import SortOptions
from src.dependencies.permissions import PermissionChecker
from src.config.database import db_handler
from src.crud.product import (
    create_product,
    delete_product_by_id,
    get_product_by_id,
    update_product_by_id,
    get_products_paginated
)
from src.schemas.product import CreateProduct, ProductOut, ProductPaginationOut
from src.config.settings import get_settings

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", name="products", response_model=ProductPaginationOut)
async def get_products_paginated_list(
    # current_user: Annotated[str, Depends(PermissionChecker(["products:view"]))],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
    limit: int = Query(**get_settings().pagination.model_dump()),
    sort_by: SortOptions = SortOptions.name_asc,
    name_query: Optional[str] = None,
    cursor: Optional[str] = Query(None, description="Format: price::id or name::id"),
):
    """
    Эндпоинт для получения списка продуктов.
    Включает пагинацию (с возможностью задания лимита на стороне пользователя),
    возможность сортировки по полям name и price и фильтрации по полю name.

    Настроить базовую пагинацию можно в `config.settings.py`
    """

    # Преобразовываем и проверяем курсор курсором
    if cursor:
        try:
            val, last_id = cursor.rsplit("::", 1)
            cursor_data = (val, int(last_id))
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Incorrect cursor format")
    else:
        cursor_data = None

    products_list = await get_products_paginated(
        session=session, limit=limit, sort_by=sort_by, name_query=name_query, cursor_data=cursor_data
    )

    # Собираем следующий курсор
    if len(products_list) == limit:
        last = products_list[-1]
        val = last.name if sort_by == SortOptions.name_asc else last.price
        next_cursor = f"{val}::{last.id}"
    else:
        next_cursor = None

    return ProductPaginationOut(items=products_list, next_cursor=next_cursor)


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
