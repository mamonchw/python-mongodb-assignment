# main.py
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
from dateutil.parser import parse
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from db import employees_coll, ensure_indexes
from models import EmployeeCreate, EmployeeOut, EmployeeUpdate

app = FastAPI(title="Employees Assessment API")

@app.on_event("startup")
async def startup():
    await ensure_indexes()

# Helper function
def _doc_to_employee(doc) -> dict:
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
@app.post("/employees", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate):
    doc = jsonable_encoder(employee)
    doc["joining_date"] = datetime(employee.joining_date.year, employee.joining_date.month, employee.joining_date.day)
    try:
        await employees_coll.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail=f"employee_id '{employee.employee_id}' already exists")
    created = await employees_coll.find_one({"employee_id": employee.employee_id})
    return _doc_to_employee(created)

@app.get("/employees/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: str):
    doc = await employees_coll.find_one({"employee_id": employee_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _doc_to_employee(doc)

@app.put("/employees/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: str, payload: EmployeeUpdate):
    update_data = payload.dict(exclude_unset=True)
    if "joining_date" in update_data and update_data["joining_date"] is not None:
        jd = update_data["joining_date"]
        update_data["joining_date"] = datetime(jd.year, jd.month, jd.day)
    result = await employees_coll.update_one({"employee_id": employee_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    updated = await employees_coll.find_one({"employee_id": employee_id})
    return _doc_to_employee(updated)

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    result = await employees_coll.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        return JSONResponse(status_code=404, content={"success": False, "message": "Employee not found"})
    return {"success": True, "message": f"Employee {employee_id} deleted"}

# ---------------- List / Query ----------------
@app.get("/employees/all", response_model=List[EmployeeOut])
async def list_all_employees():
    cursor = employees_coll.find().sort("joining_date", 1)
    employees = [ _doc_to_employee(doc) async for doc in cursor ]
    return employees

@app.get("/employees", response_model=List[EmployeeOut])
async def list_employees(department: Optional[str] = Query(None)):
    filter_q = {"department": department} if department else {}
    cursor = employees_coll.find(filter_q).sort("joining_date", -1)
    results = []
    async for doc in cursor:
        results.append(_doc_to_employee(doc))
    return results

@app.get("/employees/avg-salary")
async def avg_salary_by_department():
    pipeline = [
        {"$addFields": {"salary": {"$toDouble": "$salary"}}},  # convert salary to number
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
        {"$project": {"_id": 0, "department": "$_id", "avg_salary": {"$round": ["$avg_salary", 2]}}},
        {"$sort": {"department": 1}}
    ]
    cursor = employees_coll.aggregate(pipeline)
    results = [doc async for doc in cursor]
    return results

@app.get("/employees/search", response_model=List[EmployeeOut])
async def search_by_skill(skill: str = Query(...)):
    query = {"skills": {"$regex": f"^{skill}$", "$options": "i"}}  # case-insensitive exact match
    cursor = employees_coll.find(query).sort("joining_date", ASCENDING)
    results = []
    async for doc in cursor:
        results.append(_doc_to_employee(doc))
    return results
