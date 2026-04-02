from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from src.core.config import settings
from typing import Any

class Database:
    # Utilizamos Any porque o Pylance tem dificuldade em inferir os tipos do Motor nativamente
    client: Any = None
    db: Any = None

db_instance = Database()

async def connect_to_mongo():
    db_instance.client = AsyncIOMotorClient(
        settings.MONGODB_URL, 
        tlsCAFile=certifi.where()
    )
    db_instance.db = db_instance.client[settings.DATABASE_NAME]
    print(f"Conectado ao MongoDB: {settings.DATABASE_NAME}")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        print("Conexão com MongoDB encerrada.")

def get_database():
    return db_instance.db