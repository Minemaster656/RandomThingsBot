import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

from sqlalchemy.future import select

import CABLY
import logger

DATABASE_URL = "sqlite+aiosqlite:///./automod_cache.db"

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание сессии
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


# Определение модели
class Cache(Base):
    __tablename__ = "cache"

    string = Column(Text, primary_key=True)
    sexual = Column(Integer)
    hate = Column(Integer)
    harassment = Column(Integer)
    self_harm = Column(Integer)
    sexual_minors = Column(Integer)
    hate_threatening = Column(Integer)
    violence_graphic = Column(Integer)
    self_harm_intent = Column(Integer)
    self_harm_instructions = Column(Integer)
    harassment_threatening = Column(Integer)
    violence = Column(Integer)


# Функция для создания таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def moderate(string):
    async with async_session() as session:
        result = await session.execute(select(Cache).where(Cache.string == string))
        data = result.scalars().first()
        if not data:
            await logger.log(f"Automod cache miss: {string}")
            try:
                mod_data = await CABLY.moderate(string)
            except:
                await logger.log("Automod cache fucked up: CABLY call failed", logger.LogLevel.ERROR)
                return None
            # async with session.begin():
            if mod_data:
                cache = Cache(
                    string=string,
                    sexual=int(mod_data['sexual']),
                    hate=int(mod_data['hate']),
                    harassment=int(mod_data['harassment']),
                    self_harm=int(mod_data['self_harm']),
                    sexual_minors=int(mod_data['sexual_minors']),
                    hate_threatening=int(mod_data['hate_threatening']),
                    violence_graphic=int(mod_data['violence_graphic']),
                    self_harm_intent=int(mod_data['self_harm_intent']),
                    self_harm_instructions=int(mod_data['self_harm_instructions']),
                    harassment_threatening=int(mod_data['harassment_threatening']),
                    violence=int(mod_data['violence'])
                )
            else:
                cache = Cache(
                    string=string,
                    sexual=0,
                    hate=0,
                    harassment=0,
                    self_harm=0,
                    sexual_minors=0,
                    hate_threatening=0,
                    violence_graphic=0,
                    self_harm_intent=0,
                    self_harm_instructions=0,
                    harassment_threatening=0,
                    violence=0
                )

            session.add(cache)
            await session.commit()
            return mod_data
        else:
            await logger.log(f"Automod cache hit: {string}")
            # if everything in data excluding field string is 0 -> return None
            # else return data
            if data.sexual == 0 and data.hate == 0 and data.harassment == 0 and data.self_harm == 0 and \
                    data.sexual_minors == 0 and data.hate_threatening == 0 and data.violence_graphic == 0 and \
                    data.self_harm_intent == 0 and data.self_harm_instructions == 0 and \
                    data.harassment_threatening == 0 and data.violence == 0:
                return None
            return {
                'sexual': bool(data.sexual),
                'hate': bool(data.hate),
                'harassment': bool(data.harassment),
                'self_harm': bool(data.self_harm),
                'sexual_minors': bool(data.sexual_minors),
                'hate_threatening': bool(data.hate_threatening),
                'violence_graphic': bool(data.violence_graphic),
                'self_harm_intent': bool(data.self_harm_intent),
                'self_harm_instructions': bool(data.self_harm_instructions),
                'harassment_threatening': bool(data.harassment_threatening),
                'violence': bool(data.violence),
            }
