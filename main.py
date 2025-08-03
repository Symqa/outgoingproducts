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

@app.get("/api/products/{tg_id}")
async def products(tg_id: int):
    user = await rq.add_user(tg_id)
    return await rq.get_products(tg_id)

@app.get("/api/main/{tg_id}")
async def profile(tg_id: int):
    user = await rq.add_user(tg_id)
    products_count = await rq.get_products_count(user.id)
    return {'CountProducts': products_count}


@app.get("/api/get_user/{tg_id}")
async def get_user(tg_id: int):
    return await rq.get_user_validate(tg_id)

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

@app.get("/api/profile/change/{tg_id}")
async def update_profile(tg_id: int, time: int):
    await rq.update_user_time(tg_id, time)
    