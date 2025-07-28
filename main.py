from contextlib import asynccontextmanager

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import init_db
import requests as rq


class AddProduct(BaseModel):
    id: int
    name: str
    user: int

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
    return await rq.get_products(user.id)

@app.get("/api/main/{tg_id}")
async def profile(tg_id: int):
    user = await rq.add_user(tg_id)
    products_count = await rq.get_products_count(user.id)
    return {'CountProducts': products_count}

@app.get("/api/add")
async def add_product(product: AddProduct):
    user = await rq.add_user(product.user)
    await rq.add_product(user.id, product.name)
    return {'status': 'ok'}