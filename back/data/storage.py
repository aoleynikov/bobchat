from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector
from config import config

Base = declarative_base()

class Participant(Base):
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    messages = relationship("Message", back_populates="participant")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    participant_id = Column(Integer, ForeignKey('participants.id'))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    participant = relationship("Participant", back_populates="messages")

class DataChunk(Base):
    __tablename__ = 'data_chunks'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    chunk_index = Column(Integer, index=True)
    chunk_text = Column(Text)
    embedding = Column(Vector(1536))  # OpenAI embeddings are 1536 dimensions
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Database setup
engine = create_engine(config.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def repopulate_data_chunks(data_chunks: list):
    db = SessionLocal()
    
    new_chunks = []
    for chunk in data_chunks:
        # Use raw SQL with pgvector cosine distance function
        embedding_str = '[' + ','.join(map(str, chunk.embedding)) + ']'
        result = db.execute(
            text(f"SELECT id FROM data_chunks WHERE embedding <=> '{embedding_str}'::vector < 0.01 LIMIT 1")
        ).fetchone()
        
        if not result:
            new_chunks.append(chunk)
    
    for chunk in new_chunks:
        db.add(chunk)
    
    db.commit()
    print(f"Added {len(new_chunks)} new chunks (skipped {len(data_chunks) - len(new_chunks)} existing)")
    db.close()
