import json
from typing import Union, Optional, Type
import asyncio

import ollama
from sqlalchemy import Column, String, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Cache(Base):
    __tablename__ = 'cache'
    string = Column(String, primary_key=True)
    vector = Column(Text)

# Используем асинхронный движок для SQLite
engine = create_async_engine('sqlite+aiosqlite:///nomic_embeds_cache_async.db', echo=False)
oclient = ollama.AsyncClient(host='localhost')
# Создаем асинхронную сессию
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def find_by_string(search_string: str) -> Optional[Type[Cache]]:
    """Internal function to find cache entry by string"""
    async with async_session() as session:
        result = await session.execute(select(Cache).filter(Cache.string == search_string))
        return result.scalars().first()

async def add_new_entry(string: str, vector: list) -> None:
    """Internal function to add new cache entry"""
    async with async_session() as session:
        new_entry = Cache(string=string, vector=json.dumps(vector))
        session.add(new_entry)
        await session.commit()

async def get_embedding(text: str, print_exceptions: bool = False) -> Union[list, None]:
    """Gets string and returns its 768Dim embedding as list of floats. If it exists in cache, takes it. If gets error, returns None."""
    try:
        cached_result = await find_by_string(text)
        if cached_result:
            return json.loads(cached_result.vector)
        embedding = await oclient.embeddings(model='nomic-embed-text', prompt=text,options={"num_thread": 4})
        await add_new_entry(text, embedding['embedding'])
        return embedding['embedding']
    except Exception as e:
        if print_exceptions:
            print(e)
        return None

# Пример использования
async def main():
    await init_db()
    embedding = await get_embedding("example text")
    print(embedding)

# Запуск асинхронного main
asyncio.run(main())