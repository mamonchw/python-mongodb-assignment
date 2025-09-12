# populate_employees.py
import asyncio
from datetime import datetime
from db import employees_coll

# Sample employees
sample_employees = [
    {
        "employee_id": "E001",
        "name": "John Doe",
        "department": "Engineering",
        "salary": 75000,
        "joining_date": datetime(2023, 1, 15),
        "skills": ["Python", "MongoDB", "APIs"]
    },
    {
        "employee_id": "E002",
        "name": "Jane Smith",
        "department": "HR",
        "salary": 60000,
        "joining_date": datetime(2022, 11, 1),
        "skills": ["Recruitment", "Communication"]
    },
    {
        "employee_id": "E003",
        "name": "Alice Johnson",
        "department": "Engineering",
        "salary": 80000,
        "joining_date": datetime(2023, 5, 20),
        "skills": ["Python", "FastAPI"]
    },
    {
        "employee_id": "E004",
        "name": "Bob Williams",
        "department": "CSE",
        "salary": 70000,
        "joining_date": datetime(2024, 3, 10),
        "skills": ["FastAPI", "APIs"]
    },
    {
        "employee_id": "E005",
        "name": "Mamon Chowdhury",
        "department": "CSE",
        "salary": 72000,
        "joining_date": datetime(2025, 9, 12),
        "skills": ["FastAPI", "MongoDB"]
    }
]

async def populate():
    # Optional: clear existing collection
    await employees_coll.delete_many({})
    print("Cleared existing employees collection.")

    # Insert sample data
    result = await employees_coll.insert_many(sample_employees)
    print(f"Inserted {len(result.inserted_ids)} sample employees.")

if __name__ == "__main__":
    asyncio.run(populate())
