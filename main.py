from contextlib import asynccontextmanager

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import init_db
import requests as rq

@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Bot is ready')
    yield

app = FastAPI(title="Свежести и Тухлости")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/api/products/{tg_id}")
async def tasks(tg_id: int):
    user = await rq.add_user(tg_id)
    return await rq.get_products(user.id)

@app.get("/api/main/{tg_id}")
async def profile(tg_id: int):
    user = await rq.add_user(tg_id)
    products_count = await rq.get_products_count(user.id)
    return {'CountProducts': products_count}