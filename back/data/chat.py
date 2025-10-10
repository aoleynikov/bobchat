from sqlalchemy.orm import Session
from .storage import Participant, Message

class Chat:
    def __init__(self, db: Session):
        self.db = db
    
    def get_messages(self):
        messages = self.db.query(Message).order_by(Message.timestamp).all()
        return [self._serialize_message(msg) for msg in messages]
    
    def post_message(self, text: str, participant_name: str = "user"):
        participant = self._get_or_create_participant(participant_name)
        
        message = Message(content=text, participant_id=participant.id)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return self._serialize_message(message)
    
    def _get_or_create_participant(self, name: str):
        participant = self.db.query(Participant).filter(Participant.name == name).first()
        if not participant:
            participant = Participant(name=name)
            self.db.add(participant)
            self.db.commit()
            self.db.refresh(participant)
        return participant
    
    def _serialize_message(self, message: Message):
        return {
            'id': message.id,
            'content': message.content,
            'participant_name': message.participant.name,
            'timestamp': message.timestamp.isoformat()
        }
