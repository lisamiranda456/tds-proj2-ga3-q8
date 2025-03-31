import httpx
import os
from typing import Dict, Any
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Dict, Any # These are for type hints
from fastapi.middleware.cors import CORSMiddleware

# Configure logging (do this once at the beginning of your app)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Imxpc2EubWlyYW5kYUBncmFtZW5lci5jb20ifQ.nvcT6zt6b65Hf-rJE1Q0bwn4KrAeGzGZ6lCi5RP3IhY"  # Replace with your actual API key

load_dotenv()
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket_status",
            "description": "Get the status of a particular ticket using it's ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "integer",
                        "description": "Ticket ID number"
                    }
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
            "description": "Schedule a meeting room for a specific date and time",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Meeting date in YYYY-MM-DD format"
                    },
                    "time": {
                        "type": "string",
                        "description": "Meeting time in HH:MM format"
                    },
                    "meeting_room": {
                        "type": "string",
                        "description": "Name of the meeting room"
                    }
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
            "description": "Get expense balance for an employee",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer",
                        "description": "Employee ID number"
                    }
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
            "description": "Calculate yearly performance bonus for an employee",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer",
                        "description": "Employee ID number"
                    },
                    "current_year": {
                        "type": "integer",
                        "description": "Year to calculate bonus for"
                    }
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
            "description": "Report an office issue for a specific department",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_code": {
                        "type": "integer",
                        "description": "Employee ID number"
                    },
                    "department": {
                        "type": "string",
                        "description": "Department to to report issue for"
                    }
                },
                "required": ["issue_code", "department"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

@app.get("/execute")
async def query_gpt(user_input: str = Query(None, alias="q")) -> Dict[str, Any]:
    response = httpx.post(
        "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('AIPROXY_TOKEN')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": user_input}],
            "tools": tools,
            "tool_choice": "auto",
        },
    )
    output_msg = response.json()["choices"][0]["message"]
    return output_msg["tool_calls"][0]["function"]

# --- Run the FastAPI App ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
