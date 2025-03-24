from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import re
from typing import Dict, Any
import base64
import requests
import os
import numpy as np
from itertools import combinations
import openai
import tiktoken
from dotenv import load_dotenv

load_dotenv()  
app = FastAPI()

# Enable CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Function definitions (simulated responses for now)
def get_ticket_status(ticket_id: int) -> Dict[str, Any]:
    return {"ticket_id": ticket_id, "status": "In Progress"}

def schedule_meeting(date: str, time: str, meeting_room: str) -> Dict[str, Any]:
    return {"date": date, "time": time, "meeting_room": meeting_room, "confirmation": "Meeting scheduled"}

def get_expense_balance(employee_id: int) -> Dict[str, Any]:
    return {"employee_id": employee_id, "balance": 2500.75}

def calculate_performance_bonus(employee_id: int, current_year: int) -> Dict[str, Any]:
    return {"employee_id": employee_id, "year": current_year, "bonus": 5000}

def report_office_issue(issue_code: int, department: str) -> Dict[str, Any]:
    return {"issue_code": issue_code, "department": department, "status": "Reported"}

# Function calling tools definition
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket_status",
            "description": "Get the status of an IT support ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer", "description": "Ticket ID number"}
                },
                "required": ["ticket_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedule a meeting for a specific date and time",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Meeting date (YYYY-MM-DD)"},
                    "time": {"type": "string", "description": "Meeting time (HH:MM)"},
                    "meeting_room": {"type": "string", "description": "Meeting room name"}
                },
                "required": ["date", "time", "meeting_room"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expense_balance",
            "description": "Get the expense balance for an employee",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "Employee ID number"}
                },
                "required": ["employee_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_performance_bonus",
            "description": "Calculate the yearly performance bonus for an employee",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "Employee ID number"},
                    "current_year": {"type": "integer", "description": "Year to calculate bonus for"}
                },
                "required": ["employee_id", "current_year"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "report_office_issue",
            "description": "Report an office issue to a specific department",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_code": {"type": "integer", "description": "Issue code number"},
                    "department": {"type": "string", "description": "Department responsible"}
                },
                "required": ["issue_code", "department"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

# Function to parse user query and map it to the correct function
def parse_query(q: str):
    patterns = [
        (r"status of ticket (\d+)", get_ticket_status, ["ticket_id"]),
        (r"Schedule a meeting on (\d{4}-\d{2}-\d{2}) at (\d{2}:\d{2}) in (.+)", schedule_meeting, ["date", "time", "meeting_room"]),
        (r"Show my expense balance for employee (\d+)", get_expense_balance, ["employee_id"]),
        (r"Calculate performance bonus for employee (\d+) for (\d{4})", calculate_performance_bonus, ["employee_id", "current_year"]),
        (r"Report office issue (\d+) for the (.+) department", report_office_issue, ["issue_code", "department"]),
    ]

    for pattern, function, param_keys in patterns:
        match = re.search(pattern, q)
        if match:
            param_values = match.groups()
            params = dict(zip(param_keys, map(lambda v: int(v) if v.isdigit() else v, param_values)))
            return {"name": function.__name__, "arguments": json.dumps(params), "response": function(**params)}

    return {"error": "Query not recognized"}

@app.get("/execute")
def execute(q: str = Query(..., description="Query containing the request")):
    return parse_query(q)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)