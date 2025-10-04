from openai import OpenAI
from config import config

class LLMWrapper:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_KEY)
        self.model = config.OPENAI_MODEL
    
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

# Global instance
llm = LLMWrapper()
