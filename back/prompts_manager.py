import os
from typing import Dict, Any

class PromptsManager:
    def __init__(self, prompts_dir: str = 'prompts'):
        self.prompts_dir = prompts_dir
    
    def render(self, name: str, args: Dict[str, Any]) -> str:
        prompt_path = os.path.join(self.prompts_dir, f'{name}.txt')
        
        with open(prompt_path, 'r') as f:
            template = f.read()
        
        return template.format(**args)

# Global instance
prompts = PromptsManager()
