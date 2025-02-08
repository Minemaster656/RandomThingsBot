import json
from typing import Union, Optional, Type

import ollama
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Cache(Base):
    __tablename__ = 'cache'
    string = Column(String, primary_key=True)
    vector = Column(Text)


engine = create_engine('sqlite:///nomic_embeds_cache.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def find_by_string(search_string: str) -> Optional[Type[Cache]]:
    """Internal function to find cache entry by string"""
    result = session.query(Cache).filter(Cache.string == search_string).first()
    return result


def add_new_entry(string: str, vector: list) -> None:
    """Internal function to add new cache entry"""
    new_entry = Cache(string=string, vector=str(vector))
    session.add(new_entry)
    session.commit()


def get_embedding(text: str, print_exceptions: bool = False) -> Union[list, None]:
    """Gets string and returns its 768Dim embedding as list of floats. If it exists in cache, takes it. If gets error, returns None."""
    try:
        cached_result = find_by_string(text)
        if cached_result:

            return json.loads(str(cached_result.vector))
        embedding = ollama.embeddings(model='nomic-embed-text', prompt=text)
        add_new_entry(text, embedding.embedding)
        return embedding.embedding
    except Exception as e:
        if print_exceptions:
            print(e)
        return None
