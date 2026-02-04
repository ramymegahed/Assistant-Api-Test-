from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from assistants import ASSISTANTS
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    assistant: str

@app.post("/chat")
def chat(req: ChatRequest):

    if req.assistant not in ASSISTANTS:
        return {"reply": "المساعد ده مش موجود"}

    assistant_id = ASSISTANTS[req.assistant]["id"]
    assistant_name = ASSISTANTS[req.assistant]["name"]

    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=req.message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value

    return {
        "assistant": assistant_name,
        "reply": reply
    }

# run with:
# uvicorn main:app --reload
