# BobChat

A RAG (Retrieval-Augmented Generation) powered chat application that answers questions based on ingested documents using OpenAI embeddings and vector search.

## Overview

BobChat is a full-stack application that combines:
- **FastAPI backend** with RAG processing
- **React frontend** for chat interface
- **PostgreSQL with pgvector** for vector storage and similarity search
- **OpenAI API** for embeddings and chat completions

When you ask a question, the system retrieves relevant document chunks, includes conversation history, and generates contextual responses using an LLM.

## Features

- Chat interface with real-time message polling
- RAG-powered responses based on ingested documents
- Conversation history awareness (last 5 messages)
- File-based chat persistence (`chat.txt`)
- Clear chat functionality
- Docker Compose setup for easy deployment

## Architecture

- **Backend**: FastAPI application with `/messages` endpoints
- **Frontend**: React app with polling mechanism
- **Database**: PostgreSQL with pgvector extension for vector similarity search
- **Storage**: Chat messages stored in `chat.txt`, document chunks in PostgreSQL

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Setup

1. **Clone the repository** (if applicable)

2. **Configure environment variables**:
   ```bash
   cd back
   cp env.example .env
   ```
   
   Edit `.env` and set your OpenAI API key:
   ```
   OPENAI_KEY=your_openai_api_key_here
   ```

3. **Start the services**:
   ```bash
   cd back
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - FastAPI backend (port 8000)
   - React frontend (port 3000)

4. **Ingest documents** (first time setup):
   ```bash
   docker-compose exec chat-backend python cli.py ingest
   ```
   
   This processes documents from `back/data/files/` and stores them as vector embeddings.

## Usage

1. **Access the frontend**: Open `http://localhost:3000` in your browser

2. **Start chatting**: Type a message and press Enter or click Send

3. **View responses**: The assistant response will appear automatically after processing (typically a few seconds)

4. **Clear chat**: Click the "Clear" button to delete all messages and start fresh

## API Endpoints

- `GET /messages` - Retrieve all chat messages
- `POST /messages` - Create a new user message (triggers RAG processing in background)
- `DELETE /messages` - Clear all messages

## How It Works

1. User sends a message via the frontend
2. Backend immediately returns 201 response
3. RAG processor runs in background thread:
   - Retrieves relevant document chunks using vector similarity search
   - Includes last 5 messages as conversation history
   - Generates response using OpenAI with context
   - Adds assistant message to chat
4. Frontend polls every 5 seconds to fetch new messages
5. Assistant response appears in the UI

## Project Structure

```
bobchat/
├── back/                 # FastAPI backend
│   ├── app.py           # Main FastAPI application
│   ├── rag.py           # RAG processor
│   ├── llm.py           # OpenAI wrapper
│   ├── data/
│   │   ├── chat.py      # Chat message storage
│   │   ├── storage.py   # Database models
│   │   └── files/       # Documents to ingest
│   ├── templates/       # Jinja2 templates
│   └── docker-compose.yml
└── front/               # React frontend
    └── src/
        └── App.js       # Main chat component
```

## Development

The backend uses hot-reload via uvicorn, and the frontend uses React's development server. Changes to code will automatically reload.

To stop all services:
```bash
docker-compose down
```

To view logs:
```bash
docker-compose logs -f
```

