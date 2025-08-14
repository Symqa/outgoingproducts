from contextlib import asynccontextmanager

from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import json

from models import init_db
import requests_db as rq


class AddProduct(BaseModel):
    image: object
    data: str

class UserTimeUpdate(BaseModel):
    user_id: int
    time: int

@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Bot is ready')
    yield

app = FastAPI(title="Свежести и Тухлости", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/api/products/{tg_id}/{shop}")
async def products(tg_id: int, shop: str):
    user = await rq.add_user(tg_id)
    return await rq.get_products(tg_id, shop)


@app.get("/api/delete/{product_id}")
async def product_to_delete(product_id: int):
    await rq.delete_product(product_id)


@app.get("/api/main/{tg_id}")
async def profile(tg_id: int):
    user = await rq.add_user(tg_id)
    products_count = await rq.get_products_count(user.id)
    return {'CountProducts': products_count}


@app.get("/api/get_user/{tg_id}")
async def get_user(tg_id: int):
    user = await rq.get_user_validate(tg_id)
    count_products = await rq.get_products_count(tg_id)
    return {'user': user, 'count_products': count_products}

@app.post("/api/add")
async def add_product(product: Annotated[AddProduct, Form()]):

    data = json.loads(product.data)
    
    # with open('test.png', 'wb') as file:
    #     content = await product.image.read()
    #     file.write(content)
    
    user = await rq.add_user(data['user'])
    await rq.add_product(user.id,
                        data['name'],
                        data['count'],
                        data['produced'],
                        data['expire'],
                        data['category'],
                        data['shop'],
                        product.image)
    return {'status': '200'}

@app.post("/api/profile/change")
async def update_profile(userTime: UserTimeUpdate):
    print(userTime)
    await rq.update_user_time(userTime.user_id, userTime.time)
    return {'status': '200'}
    