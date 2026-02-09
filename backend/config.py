import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or (
        f"postgresql://{os.getenv('POSTGRES_USER', 'upao_user')}"
        f":{os.getenv('POSTGRES_PASSWORD', 'upao_secret_2024')}"
        f"@{os.getenv('POSTGRES_HOST', 'localhost')}"
        f":{os.getenv('POSTGRES_PORT', '5433')}"
        f"/{os.getenv('POSTGRES_DB', 'upao_rag')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ollama
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemma3:4b')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')

    # Qdrant
    QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
    QDRANT_PORT = int(os.getenv('QDRANT_PORT', '6333'))
    QDRANT_COLLECTION = os.getenv('QDRANT_COLLECTION', 'upao_documents')

    # RAG
    RAG_CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', '1000'))
    RAG_CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', '200'))
    RAG_TOP_K = int(os.getenv('RAG_TOP_K', '5'))
    RAG_SCORE_THRESHOLD = float(os.getenv('RAG_SCORE_THRESHOLD', '0.35'))
    RAG_TEMPERATURE = float(os.getenv('RAG_TEMPERATURE', '0.3'))
    RAG_NUM_CTX = int(os.getenv('RAG_NUM_CTX', '4096'))

    # Upload
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '80'))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'xls', 'txt', 'png', 'jpg', 'jpeg'}

    # Admin seed
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@upao.edu.pe')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Clave123')
    ADMIN_FULL_NAME = os.getenv('ADMIN_FULL_NAME', 'Administrador')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
}
