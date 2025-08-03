from sqlalchemy import select, update, delete, func
from models import async_session, User, Product
from pydantic import BaseModel, ConfigDict, model_validator
from typing import List
import requests
import datetime
import base64

class ProductSchema(BaseModel):

    id: int
    user: int
    name: str
    count: int
    produced: str
    expire: str
    category: str
    shop: str
    image: str
    user_time: int

    @model_validator(mode='after')
    def change_produced_time(self):

        offset_days = 3 + self.user_time
        offset = datetime.timedelta(hours=offset_days)

        date_time_produced = datetime.datetime.fromisoformat(self.produced)
        date_time_expire = datetime.datetime.fromisoformat(self.expire)

        new_time_produced = date_time_produced + offset
        new_time_expire = date_time_expire + offset

        self.produced = new_time_produced.isoformat()
        self.expire = new_time_expire.isoformat()
        
        return self
    
    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: int
    tg_id: int
    time: int

    model_config = ConfigDict(from_attributes=True)


async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user
        
        new_user = User(tg_id=tg_id, time='0')
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def get_user_validate(tg_id):
    user = await add_user(tg_id)
    serialized_user = UserSchema.model_validate(user).model_dump()
    return serialized_user


async def get_products(user_id):
    async with async_session() as session:
        products = await session.scalars(
            select(Product).where(Product.user == user_id)
        )

        serialized_products = [
            ProductSchema.model_validate(p).model_dump() for p in products
        ]
        print(serialized_products)
        return serialized_products


async def get_products_count(user_id):
    async with async_session() as session:
        return await session.scalar(select(func.count(Product.id)).where(Product.id == user_id))
    
async def add_product(user_id, name, count, produced, expire, category, shop, image):
    async with async_session() as session:
        user = await add_user(user_id)
        user_time = user.time

        produced_datetime = datetime.datetime(
            produced['year'],
            produced['month'],
            produced['day'],
            produced['hour'],
            produced['minutes'],
            0
        )

        expire_datetime = datetime.datetime(
            expire['year'],
            expire['month'],
            expire['day'],
            expire['hour'],
            expire['minutes']
        )
        try:
            image_binary = base64.b64encode(await image.read()).decode('utf-8')
        except Exception as e:
            print('Не удалось обработать картинку. \n Ошибка: ', e)
            return 
        
        new_product = Product(
            name=name,
            user=user_id,
            count=count,
            produced=produced_datetime.isoformat(),
            expire=expire_datetime.isoformat(),
            category=category,
            shop=shop,
            image="data:image/png;base64," + image_binary,
            user_time=user_time
        )
        session.add(new_product)
        await session.commit()

        

async def update_user_time(tg_id, time):
    async with async_session() as session:
        user = await add_user(tg_id)
        user.time = time
        await session.flush()
        await session.commit()

async def get_product_by_id(product_id):
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.id == product_id))
        if product:
            return product
