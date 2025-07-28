from sqlalchemy import select, update, delete, func
from models import async_session, User, Product
from pydantic import BaseModel, ConfigDict
from typing import List

class ProductSchema(BaseModel):

    id: int
    name: str
    user: int
    #produced
    #expritation_date
    #photo
    #count
    #category

    model_config = ConfigDict(from_attributes=True)


async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user
        
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def get_products(user_id):
    async with async_session() as session:
        products = await session.scalars(
            select(Product).where(Product.user == user_id)
        )

        serialized_products = [
            ProductSchema.model_validate(p).model_dump() for p in products
        ]

        return serialized_products

async def get_products_count(user_id):
    async with async_session() as session:
        return await session.scalar(select(func.count(Product.id)).where(Product.id == user_id))
    
async def add_product(user_id, name):
    async with async_session() as session:
        new_product = Product(
            name=name,
            user=user_id
        )
        session.add(new_product)
        await session.commit()