from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class TemplateManager:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
    
    def render_rag_prompt(self, question: str, chunks: list, messages: list = []) -> str:
        template = self.env.get_template("rag_prompt.j2")
        return template.render(
            question=question, 
            chunks=chunks, 
            messages=messages
        )