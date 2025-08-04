from sqlalchemy import ForeignKey, String, BigInteger, DateTime, BLOB, LargeBinary
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    time: Mapped[int]

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(50))
    count: Mapped[int]
    produced: Mapped[str] = mapped_column(String(100))
    expire: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    shop: Mapped[str] = mapped_column(String(50))
    image: Mapped[str] = mapped_column(String())
    user_time: Mapped[int]
    progress_percent: Mapped[int]
    progress_color: Mapped[str] = mapped_column(String(50))
    is_50: Mapped[bool]
    is_25: Mapped[bool]
    is_10: Mapped[bool]
    is_bad: Mapped[bool]

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#produced
#expritation_date
#photo
#count
#category