"""Initial commit

Revision ID: 91c88a7508dd
Revises: 90db1b1c7d8b
Create Date: 2026-04-17 23:27:24.212071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91c88a7508dd'
down_revision: Union[str, Sequence[str], None] = '90db1b1c7d8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаем Enum тип (укажите все статусы, которые есть в вашем классе CartStatus)
    status_enum = sa.Enum('CURRENT', 'ORDERED', 'IN_PROGRESS', 'COMPLETED', name='cartstatus')
    status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Добавляем колонку status (только ОДИН раз)
    op.add_column('carts', sa.Column('status', status_enum, nullable=False))

    # 3. Остальные поля и индексы
    op.add_column('carts', sa.Column('order_at', sa.DateTime(), nullable=True))
    op.add_column('carts', sa.Column('order_amount', sa.Integer(), nullable=True))

    op.add_column('cart_products', sa.Column('product_price', sa.Float(), nullable=True))
    op.add_column('cart_products', sa.Column('product_amount', sa.Integer(), nullable=True))

    op.create_index('idx_cart_product_unique', 'cart_products', ['cart_id', 'product_id'], unique=True)

    # Удаляем старый уникальный индекс и создаем частичный (фильтруемый)
    op.drop_constraint(op.f('uq_carts_user_id'), 'carts', type_='unique')
    op.create_index(
        'idx_user_current_cart_unique',
        'carts',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text("status = 'CURRENT'")  # Убедитесь, что регистр совпадает с Enum
    )


def downgrade() -> None:
    # Удаляем индекс и колонки
    op.drop_index('idx_user_current_cart_unique', table_name='carts', postgresql_where=sa.text("status = 'CURRENT'"))
    op.drop_column('carts', 'order_amount')
    op.drop_column('carts', 'order_at')
    op.drop_column('carts', 'status')

    # Удаляем тип данных Enum
    status_enum = sa.Enum(name='cartstatus')
    status_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index('idx_cart_product_unique', table_name='cart_products')
    op.drop_column('cart_products', 'product_amount')
    op.drop_column('cart_products', 'product_price')

    # Возвращаем старый уникальный ключ
    op.create_unique_constraint(op.f('uq_carts_user_id'), 'carts', ['user_id'])
