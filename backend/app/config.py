import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

RACINE_PROJET: Path = Path(__file__).parent.parent

DB_PATH: str =str(RACINE_PROJET / "styleshop.db") # type: ignore

OPENAI_API_KEY : str = os.getenv("OPENAI_API_KEY","")

LLM_MODEL: str = "gpt-4o-mini" # type: ignore
LLM_TEMPERATURE: float =0.3
LLM_TIMEOUT: int=30
LLM_MAX_RETRIES: int=2

MAX_MESSAGES_HISTORIQUE: int = 20

LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2",'false')
LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY","")
LANGCHAIN_PROJECT:str = os.getenv("LANGCHAIN_PROJECT","default")

