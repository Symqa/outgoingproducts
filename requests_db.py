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
    progress_percent: int
    progress_color: str
    is_50: bool
    is_25: bool
    is_10: bool
    is_bad: bool

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
        
        now_time = datetime.datetime.now(datetime.timezone.utc)

        date_time_delta = date_time_expire - date_time_produced
        now_seconds_delta = date_time_expire - now_time

        date_time_delta_seconds = date_time_delta.total_seconds()
        now_seconds_delta_seconds = now_seconds_delta.total_seconds()

        self.progress_percent = 100 - int(now_seconds_delta_seconds / date_time_delta_seconds * 100)
        if self.progress_percent > 50:
            self.progress_color = 'green'
        elif self.progress_percent < 50 and self.progress_percent > 25:
            self.progress_color = 'orange'
        else:
            self.progress_color = 'red'         

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
        
        is_50 = is_25 = is_10 = False

        now_time = datetime.datetime.now(datetime.timezone.utc)
        delta = (expire_datetime - produced_datetime).total_seconds()
        now_delta = (expire_datetime - now_time)

        percent = 100 - int(now_delta / delta * 100)

        if percent > 50:
            color = 'green'
        elif percent < 50 and percent > 25:
            color = 'orange'
            is_50 = True
        else:
            is_50 = True
            is_25 = True
            color = 'red'


        new_product = Product(
            name=name,
            user=user_id,
            count=count,
            produced=produced_datetime.isoformat(),
            expire=expire_datetime.isoformat(),
            category=category,
            shop=shop,
            image="data:image/png;base64," + image_binary,
            user_time=user_time,
            progress_percent = percent,
            progress_color=color,
            is_50 = True,
            is_25 = True,
            is_10 = True,
            is_bad = False
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
