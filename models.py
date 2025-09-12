# models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date
from dateutil.parser import parse as parse_date

class EmployeeBase(BaseModel):
    name: str
    department: str
    salary: float
    joining_date: date
    skills: List[str] = []

    @validator("joining_date", pre=True)
    def parse_joining_date(cls, v):
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return parse_date(v).date()
            except Exception:
                raise ValueError("joining_date must be a valid date string (e.g. 2023-01-15)")
        raise ValueError("Invalid joining_date")

class EmployeeCreate(EmployeeBase):
    employee_id: str = Field(..., min_length=1)

class EmployeeUpdate(BaseModel):
    name: Optional[str]
    department: Optional[str]
    salary: Optional[float]
    joining_date: Optional[date]
    skills: Optional[List[str]]

    @validator("joining_date", pre=True)
    def parse_joining_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return parse_date(v).date()
            except Exception:
                raise ValueError("joining_date must be a valid date string (e.g. 2023-01-15)")
        raise ValueError("Invalid joining_date")

class EmployeeOut(EmployeeCreate):
    pass
