from fastapi import APIRouter

from src.models.cart import Cart

router = APIRouter()


@router.get("/cart/{user_id}", response_model=Cart)
async def get_user_cart(user_id: int):
    cart =