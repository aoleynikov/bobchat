from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
from contextlib import asynccontextmanager
from data.storage import get_db, create_tables
from data.chat import Chat
from data.file_processor import FileProcessorFactory, TextFileProcessor, HTMLFileProcessor, ImageFileProcessor, EPUBFileProcessor
from config import config

# Assemble individual processors
text_processor = TextFileProcessor(chunk_size=8192)
html_processor = HTMLFileProcessor(chunk_size=8192)
image_processor = ImageFileProcessor(chunk_size=8192)

# Assemble EPUB processor with injected dependencies
epub_processor = EPUBFileProcessor(
    chunk_size=8192,
    text_processor=text_processor,
    html_processor=html_processor,
    image_processor=image_processor
)

# Assemble processors dictionary with instances
processors = {
    'text': text_processor,
    'html': html_processor,
    'image': image_processor,
    'epub': epub_processor,
}

# Create file processor factory with injected processors
file_processor_factory = FileProcessorFactory(processors)

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
    role: str = "user"

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
    return chat.post_message(message.content, message.role)

if __name__ == '__main__':
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
