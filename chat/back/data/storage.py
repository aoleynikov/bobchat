from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
from config import config

engine = create_engine(config.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Participant(Base):
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    messages = relationship('Message', back_populates='participant')

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    participant_id = Column(Integer, ForeignKey('participants.id'), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    participant = relationship('Participant', back_populates='messages')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
