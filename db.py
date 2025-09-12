# db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "assessment_db")
COLLECTION_NAME = "employees"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
employees_coll = db[COLLECTION_NAME]

async def ensure_indexes():
    """Ensure unique index on employee_id. Call during app startup."""
    await employees_coll.create_index("employee_id", unique=True)
