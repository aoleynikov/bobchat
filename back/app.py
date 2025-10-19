from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import threading
from datetime import datetime

from data.chat import Chat
from data.storage import create_tables
from rag import RAGProcessor
from llm import llm
from template_manager import TemplateManager

create_tables()

app = FastAPI(title="BobChat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class MessageCreate(BaseModel):
    content: str
    role: str = "user"

class MessageResponse(BaseModel):
    id: int
    content: str
    role: str
    timestamp: str

chat = Chat()
template_manager = TemplateManager()
rag_processor = RAGProcessor(llm, template_manager)

def process_rag_background():
    rag_response = rag_processor.process(chat)
    chat.post_message(rag_response, "assistant")
    chat.save()

@app.get("/")
async def root():
    return {"message": "BobChat API is running"}

@app.get("/messages", response_model=List[MessageResponse])
async def get_messages():
    messages = chat.get_messages()
    return messages

@app.post("/messages", response_model=MessageResponse, status_code=201)
async def create_message(message: MessageCreate):
    new_message = chat.post_message(
        text=message.content,
        role=message.role
    )
    
    thread = threading.Thread(target=process_rag_background)
    thread.daemon = True
    thread.start()
    
    return new_message

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
