import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')

    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    FAISS_INDEX_PATH = os.environ.get('FAISS_INDEX_PATH', './data/faiss.index')
    DOC_STORE_PATH = os.environ.get('DOC_STORE_PATH', './data/doc_store.pkl')


    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    OLLAMA_URL = os.environ.get('OLLAMA_URL')
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')