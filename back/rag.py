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
    
    def process(self, prompt: str) -> str:
        """Process a prompt through the RAG system and return the answer."""
        # Get relevant chunks
        relevant_chunks = self.get_relevant_chunks(prompt, limit=5)
        
        # Create RAG prompt using template manager
        rag_prompt = self.template_manager.render_rag_prompt(prompt, relevant_chunks)
        
        # Generate answer using LLM
        answer = self.llm.generate(rag_prompt)
        
        return answer