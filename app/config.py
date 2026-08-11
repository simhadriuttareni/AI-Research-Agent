import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # Model Configuration
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    
    # Database
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # Application
    APP_NAME: str = "AI Research Agent"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()