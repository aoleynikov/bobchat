from typing import List, Dict, Any
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)

class Chat:
    def __init__(self, chat_file: str = "chat.txt"):
        self.chat_file = chat_file
        self.messages = []
        self.participants = {}
        self.next_message_id = 1
        self.load()
    
    def get_messages(self):
        return sorted(self.messages, key=lambda x: x['timestamp'])
    
    def post_message(self, text: str, role: str = "user"):
        if role not in self.participants:
            self.participants[role] = len(self.participants) + 1
        
        message = {
            'id': self.next_message_id,
            'content': text,
            'role': role,
            'timestamp': datetime.now().isoformat()
        }
        
        self.messages.append(message)
        self.next_message_id += 1
        
        self.save()
        
        return message
    
    def save(self):
        chat_data = {
            'messages': self.messages,
            'participants': self.participants,
            'next_message_id': self.next_message_id
        }
        
        with open(self.chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
    
    def load(self):
        if not os.path.exists(self.chat_file):
            return
        
        with open(self.chat_file, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
        
        self.messages = chat_data.get('messages', [])
        self.participants = chat_data.get('participants', {})
        self.next_message_id = chat_data.get('next_message_id', 1)
    
    def clear_messages(self):
        self.messages = []
        self.participants = {}
        self.next_message_id = 1
        self.save()
