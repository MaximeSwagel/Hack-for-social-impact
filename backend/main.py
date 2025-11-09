import json
import logging
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resource_finder import list_eligible_resources
from typing import Dict, Any, List

# Load environment variables from the .env file
load_dotenv()

# --- 1. Initialize FastAPI and OpenAI Client ---
app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Configure logging ---
log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- 2. Configure CORS ---
# This is crucial for allowing your React frontend to communicate with this backend.
# It's a security feature that browsers enforce.
origins = [
    "http://localhost:5173",  # Default Vite React dev server
    "http://localhost:3000",  # Common Create React App dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

chat_history: Dict[str, List[Dict[str, str]]] = {"messages": []}

def search_eligible_resources(conversation_history: List[Dict[str, str]] = None,
                           breadth: int = 1,
                           depth: int = 2) -> str:
    history = conversation_history or chat_history["messages"]
    return list_eligible_resources(history, breadth=breadth, depth=depth)

class ChatInput(BaseModel):
    user_message: str

# Tool schema for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_eligible_resources",
            "description": "Return a curated list of local homeless youth housing/resources.",
            "parameters": {
                "type": "object",
                "properties": {},        # no args
                "required": [],
                "additionalProperties": False,
            },
        },
    }
]

# Map tool name -> Python function
TOOL_IMPLS: Dict[str, Any] = {
    "search_eligible_resources": search_eligible_resources,
}

@app.post("/chat")
async def chat_with_ai(input_data: ChatInput):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": input_data.user_message
            },
        ]
        chat_history["messages"].append({"role": "user", "content": input_data.user_message})

        # 1) Ask the model, advertising the tool
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # supports tool calling; use your preferred model
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",   # let the model decide
            temperature=0.2,
        )

        msg = resp.choices[0].message

        # 2) If the model wants to call tools, execute them and continue the loop once
        if getattr(msg, "tool_calls", None):
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [tc.model_dump() for tc in msg.tool_calls]})

            for tc in msg.tool_calls:
                name = tc.function.name
                args = tc.function.arguments
                # Parse args if any (ours has none)
                parsed = json.loads(args) if (args and args.strip()) else {}

                if name not in TOOL_IMPLS:
                    raise HTTPException(status_code=500, detail=f"Unknown tool requested: {name}")

                result = TOOL_IMPLS[name](**parsed) if parsed else TOOL_IMPLS[name]()

                # 3) Return the tool result back to the model
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": json.dumps(result),
                })

            # 4) Ask the model again for the final user-facing answer
            resp2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            final_text = resp2.choices[0].message.content
            chat_history["messages"].append(
                {"role": "assistant", "content": final_text or ""}
            )
            return {"bot_response": final_text}

        # No tool call: just return the model’s text
        chat_history["messages"].append(
            {"role": "assistant", "content": msg.content or ""}
        )
        return {"bot_response": msg.content}

    except Exception as e:
        logger.error(f"Error in /chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
