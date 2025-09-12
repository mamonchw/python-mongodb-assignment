# db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "assessment_db")
COLLECTION_NAME = "employees"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
employees_coll = db[COLLECTION_NAME]


employee_schema = {
    "bsonType": "object",
    "required": ["employee_id", "name", "department", "salary", "joining_date", "skills"],
    "properties": {
        "employee_id": {"bsonType": "string"},
        "name": {"bsonType": "string"},
        "department": {"bsonType": "string"},
        "salary": {"bsonType": ["double", "int"]},
        "joining_date": {"bsonType": "date"},
        "skills": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        }
    }
}

async def ensure_indexes():
    # Drop collection if you want schema to apply fresh
    # await db.drop_collection("employees")

    # Create collection with validator if not exists
    collections = await db.list_collection_names()
    if "employees" not in collections:
        await db.create_collection(
            "employees",
            validator={"$jsonSchema": employee_schema}
        )

    # Ensure unique index on employee_id
    await employees_coll.create_index("employee_id", unique=True)
