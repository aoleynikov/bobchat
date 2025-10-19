from sqlalchemy import text
from data.storage import SessionLocal

class RAGProcessor:
    def __init__(self, llm, template_manager):
        self.llm = llm
        self.template_manager = template_manager
    
    def get_relevant_chunks(self, question: str, limit: int = 5) -> list:
        """Find the most relevant chunks for a question using vector similarity."""
        db = SessionLocal()
        
        # Generate embedding for the question
        question_embedding = self.llm.generate_embedding(question)
        
        # Convert to string format for pgvector
        embedding_str = '[' + ','.join(map(str, question_embedding)) + ']'
        
        # Use pgvector to find most similar chunks
        chunks = db.execute(
            text(f"""
                SELECT filename, chunk_index, chunk_text, embedding <=> '{embedding_str}'::vector as distance
                FROM data_chunks 
                ORDER BY embedding <=> '{embedding_str}'::vector 
                LIMIT :limit
            """),
            {"limit": limit}
        ).fetchall()
        
        db.close()
        return chunks
    
    def process(self, chat) -> str:
        """Process a chat through the RAG system with conversation history."""
        # Get the last 5 messages for conversation history
        all_messages = chat.get_messages()
        last_5_messages = all_messages[-5:] if len(all_messages) > 5 else all_messages
        
        # Get the latest user message
        latest_message = last_5_messages[-1] if last_5_messages else None
        if not latest_message or latest_message['role'] != 'user':
            return "I need a user message to respond to."
        
        # Get relevant chunks for the latest message
        relevant_chunks = self.get_relevant_chunks(latest_message['content'], limit=5)
        
        # Create RAG prompt with conversation history
        rag_prompt = self.template_manager.render_rag_prompt(
            latest_message['content'], 
            relevant_chunks, 
            last_5_messages[:-1]  # Pass messages directly, excluding the latest
        )
        
        # Generate answer using LLM
        answer = self.llm.generate(rag_prompt)
        
        return answer