import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://chatuser:chatpass@localhost:5432/chatdb')
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'chatdb')
    DB_USER: str = os.getenv('DB_USER', 'chatuser')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'chatpass')
    
    # API Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_TITLE: str = os.getenv('API_TITLE', 'Chat API')
    API_VERSION: str = os.getenv('API_VERSION', '1.0.0')
    
    # CORS Configuration
    CORS_ORIGINS: list = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # OpenAI Configuration
    OPENAI_KEY: str = os.getenv('OPENAI_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Environment
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    @classmethod
    def get_database_url(cls) -> str:
        if cls.DATABASE_URL.startswith('postgresql://'):
            return cls.DATABASE_URL
        return f'postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}'
    
    @classmethod
    def validate_config(cls) -> None:
        required_vars = ['DB_PASSWORD', 'OPENAI_KEY']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise ValueError(f'Missing required environment variables: {missing_vars}')

# Create global config instance
config = Config()
