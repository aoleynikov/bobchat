from openai import OpenAI
from config import config
import tiktoken

class LLMWrapper:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_KEY)
        self.model = config.OPENAI_MODEL
        # Initialize tokenizer for token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content
    
    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
    
    def generate_embedding(self, text: str) -> list:
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

# Global instance
llm = LLMWrapper()
