from fastapi import FastAPI, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime
from dateutil.parser import parse
from pymongo.errors import DuplicateKeyError

from db import employees_coll, ensure_indexes
from models import EmployeeCreate, EmployeeOut, EmployeeUpdate

# Create the FastAPI app
app = FastAPI(title="Employees Assessment API")

# Run this when the app starts
@app.on_event("startup")
async def startup():
    # Ensure necessary indexes (like unique employee_id) are created in MongoDB
    await ensure_indexes()

# ---------------- Helper function ----------------
def _doc_to_employee(doc) -> dict:
    """
    Convert a MongoDB document to a proper employee dictionary.
    - Removes _id field
    - Ensures joining_date is always ISO date string (YYYY-MM-DD)
    """
    if not doc:
        return None
    doc.pop("_id", None)
    jd = doc.get("joining_date")
    if isinstance(jd, datetime):
        doc["joining_date"] = jd.date().isoformat()
    elif isinstance(jd, str):
        try:
            doc["joining_date"] = parse(jd).date().isoformat()
        except:
            pass
    return doc

# ---------------- CRUD ----------------

# Create a new employee
@app.post("/employees", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate):
    # Convert input to JSON-compatible dict
    doc = jsonable_encoder(employee)
    # Store joining_date as datetime in DB
    doc["joining_date"] = datetime(employee.joining_date.year, employee.joining_date.month, employee.joining_date.day)
    try:
        # Insert into DB
        await employees_coll.insert_one(doc)
    except DuplicateKeyError:
        # Handle duplicate employee_id error
        raise HTTPException(status_code=400, detail=f"employee_id '{employee.employee_id}' already exists")
    # Fetch the created employee to return
    created = await employees_coll.find_one({"employee_id": employee.employee_id})
    return _doc_to_employee(created)

# Search employees by skill
@app.get("/employees/search", response_model=List[EmployeeOut])
async def search_employees_by_skill(
    skill: str = Query(..., description="Skill to search employees by")
):
    cursor = employees_coll.find({"skills": skill})
    employees = []
    async for doc in cursor:
        employees.append(_doc_to_employee(doc))
    return employees

# Compute average salary by department
@app.get("/employees/avg-salary")
async def average_salary_by_department():
    """
    Calculate average salary grouped by department.
    Example output: [{"department": "Engineering", "average_salary": 75000.0}]
    """
    pipeline = [
        {"$group": {"_id": "$department", "average_salary": {"$avg": "$salary"}}},
        {"$sort": {"_id": 1}}
    ]
    results = await employees_coll.aggregate(pipeline).to_list(length=None)
    
    return [
        {"department": r["_id"], "average_salary": round(r["average_salary"], 2)}
        for r in results
    ]

# Get details of a single employee
@app.get("/employees/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: str):
    doc = await employees_coll.find_one({"employee_id": employee_id})
    if not doc:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="Employee not found")
    return _doc_to_employee(doc)

# Update an employee
@app.put("/employees/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: str, payload: EmployeeUpdate):
    # Take only the provided fields
    update_data = payload.dict(exclude_unset=True)
    # Convert joining_date properly if present
    if "joining_date" in update_data and update_data["joining_date"] is not None:
        jd = update_data["joining_date"]
        update_data["joining_date"] = datetime(jd.year, jd.month, jd.day)
    # Update DB record
    result = await employees_coll.update_one({"employee_id": employee_id}, {"$set": update_data})
    if result.matched_count == 0:
        # If no record was updated, employee does not exist
        raise HTTPException(status_code=404, detail="Employee not found")
    # Return updated record
    updated = await employees_coll.find_one({"employee_id": employee_id})
    return _doc_to_employee(updated)

# Delete an employee
@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    result = await employees_coll.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        # Employee not found
        return JSONResponse(status_code=404, content={"success": False, "message": "Employee not found"})
    return {"success": True, "message": f"Employee {employee_id} deleted"}

# List employees in a department
@app.get("/employees", response_model=List[EmployeeOut])
async def list_employees(
    department: str = Query(..., description="Department name to filter employees"),
    skip: int = 0,
    limit: int = 50
):
    """
    List employees in a given department.
    - Sorted by joining_date (newest first).
    - Supports pagination with skip and limit.
    Example: /employees?department=Engineering
    """
    cursor = (
        employees_coll.find({"department": department})
        .sort("joining_date", -1)  # newest first
        .skip(skip)
        .limit(limit)
    )

    employees = []
    async for doc in cursor:
        employees.append(_doc_to_employee(doc))
    return employees
