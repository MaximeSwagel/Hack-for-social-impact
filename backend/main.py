import json
import logging
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
        # Forward the user's message to the OpenAI API
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": input_data.user_message},
            ],
        )
        # Extract and return the AI's response
        bot_response = completion.choices[0].message.content
        return {"bot_response": bot_response}

    except Exception as e:
        # Properly handle potential API errors
        raise HTTPException(status_code=500, detail=str(e))