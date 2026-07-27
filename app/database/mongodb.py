from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URL = "mongodb://localhost:27018"

client = AsyncIOMotorClient(MONGO_URL)

database = client["tabfm_db"]

models_collection = database["models"]

tasks_collection = database["tasks"]