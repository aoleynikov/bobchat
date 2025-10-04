from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
from contextlib import asynccontextmanager
from data.storage import get_db, create_tables
from data.chat import Chat
from config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(title=config.API_TITLE, version=config.API_VERSION, lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class MessageCreate(BaseModel):
    content: str
    participant_name: str = "user"

@app.get('/')
async def root():
    return {'message': 'Chat API is running'}

@app.get('/health')
async def health_check():
    return {'status': 'healthy'}

@app.get('/messages')
async def get_messages(db: Session = Depends(get_db)):
    chat = Chat(db)
    return chat.get_messages()

@app.post('/messages')
async def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    chat = Chat(db)
    return chat.post_message(message.content, message.participant_name)

if __name__ == '__main__':
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
