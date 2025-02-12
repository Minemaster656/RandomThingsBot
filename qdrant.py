from qdrant_client import QdrantClient
import uuid
from qdrant_client.http import models

from private import coreData

# Подключение к локальному серверу Qdrant
client = QdrantClient(url=coreData.qdrant_url+":"+str(coreData.qdrant_port), api_key=coreData.qdrant_api_key)

collection_name = "aplr_mem"

# Проверяем, существует ли коллекция
if not client.collection_exists(collection_name):
    print(f"Коллекция '{collection_name}' не найдена. Создаем...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config={"size": 768, "distance": "Cosine"},  # Задаем размерность и метрику
    )

def add_memories(agentID:str, payload:dict, timestamp:float, locationID:str):
    """

    agentID is str id of agent that knows it (characterID:str)
    Timestamp is UNIX sec timestamp (int)
    Payload is {chunk:str : vector:list of float by nomic-text-embeddings from embedder.
    LocationID is str id of location (locationID:str)
    ---
    :returns: dict of points uuids (str): chunk_string : uuid
    """
    points = []
    uuids = {}
    for chunk, vector in payload.items():
        UUID = str(uuid.uuid4())
        uuids[chunk]=UUID
        points.append({
            "id": UUID,
            "vector": vector,
            "payload": {
                "agent": agentID,
                "chunk": chunk,
                "timestamp": timestamp,
                "location": locationID
            }
        })
    try:
        result = client.upsert(
            collection_name=collection_name,
            points=points
        )
    except:
        return None
    return uuids

def get_memories_by_chunks_uuids(agentID:str, chunk_uuids:list,entries_per_chunk:int=3):
    chunks_points = client.retrieve(
    collection_name=collection_name,  # Замените на имя вашей коллекции
    ids=chunk_uuids,
    with_vectors=True,  # Указываем, что нужно вернуть вектора
    with_payload=False,

    )
    result = {}
    for record in chunks_points:
        vector = record.vector
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="agent",
                    match=models.MatchValue(value=agentID)
                )
            ]
        )

        # Выполнение поиска
        search_result = client.query_points(
            collection_name=collection_name,
            query=vector,
            query_filter=query_filter,
            limit=entries_per_chunk
        )
        # print(search_result)

        for doc in search_result.points:
            print(doc)
            result[doc.id] = doc.payload

    return result