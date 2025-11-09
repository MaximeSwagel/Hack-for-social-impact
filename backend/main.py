import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- 1. Initialize FastAPI and OpenAI Client ---
app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# --- 3. Define the Request Data Structure ---
# Pydantic model ensures the incoming data has the correct format.
class ChatInput(BaseModel):
    user_message: str


def listall():
    """Temporary placeholder until the tool is fully implemented."""
    return {
        "providers": [
            {
                "name": "Example Transitional Housing",
                "website": "https://example.org",
                "description": "Placeholder response from listall().",
            }
        ]
    }


# --- 4. Create API Endpoints ---
@app.get("/")
async def health_check():
    """A simple endpoint to confirm the server is running."""
    return {"status": "ok"}

@app.post("/chat")
async def chat_with_ai(input_data: ChatInput):
    """The main endpoint to handle chat interactions."""
    try:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "listall",
                    "description": "Return SF homeless youth housing resources.",
                    "parameters": {"type": "object"},
                },
            }
        ]

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": input_data.user_message},
            ],
            tools=tools,
        )

        while getattr(response, "required_action", None):
            tool_calls = response.required_action.submit_tool_outputs.tool_calls
            outputs = []

            for call in tool_calls:
                if call.function.name != "listall":
                    raise ValueError(f"Unsupported tool: {call.function.name}")

                outputs.append(
                    {
                        "tool_call_id": call.id,
                        "output": json.dumps(listall()),
                    }
                )

            response = client.responses.submit_tool_outputs(
                response_id=response.id,
                tool_outputs=outputs,
            )

        bot_response = response.output[0].content[0].text.value.strip()
        return {"bot_response": bot_response}

    except Exception as e:
        # Properly handle potential API errors
        raise HTTPException(status_code=500, detail=str(e))
