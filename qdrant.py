from qdrant_client import QdrantClient
import uuid

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

def add_memory(agentID:str, vector:list, chunk:str, timestamp:str, location:str):
    client.upsert(
        collection_name=collection_name,
        points=[
            {
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "agent": agentID,
                    "chunk": chunk,
                    "timestamp": timestamp,
                    "location": location
                }


            }
        ],
    )