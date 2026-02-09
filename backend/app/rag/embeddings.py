from langchain_ollama import OllamaEmbeddings
from flask import current_app


_embeddings_instance = None


def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = OllamaEmbeddings(
            model=current_app.config['EMBEDDING_MODEL'],
            base_url=current_app.config['OLLAMA_BASE_URL'],
        )
    return _embeddings_instance
