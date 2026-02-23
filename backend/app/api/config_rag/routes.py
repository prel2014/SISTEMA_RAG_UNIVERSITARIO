from flask import Blueprint, request, current_app
from app.middleware.role_required import role_required
from app.utils.response import success_response, error_response

config_rag_bp = Blueprint('config_rag', __name__)

# In-memory config overrides (resets on restart, persists via env vars)
_rag_config_overrides = {}


def get_rag_config():
    config = {
        'chunk_size': current_app.config.get('RAG_CHUNK_SIZE', 1000),
        'chunk_overlap': current_app.config.get('RAG_CHUNK_OVERLAP', 200),
        'top_k': current_app.config.get('RAG_TOP_K', 5),
        'score_threshold': current_app.config.get('RAG_SCORE_THRESHOLD', 0.35),
        'temperature': current_app.config.get('RAG_TEMPERATURE', 0.3),
        'num_ctx': current_app.config.get('RAG_NUM_CTX', 4096),
        'llm_model': current_app.config.get('LLM_MODEL', 'gemma3:4b'),
        'embedding_model': current_app.config.get('EMBEDDING_MODEL', 'nomic-embed-text'),
        'candidate_multiplier': current_app.config.get('RAG_CANDIDATE_MULTIPLIER', 4),
        'max_chunks_per_doc': current_app.config.get('RAG_MAX_CHUNKS_PER_DOC', 2),
        'enable_reflection': current_app.config.get('RAG_ENABLE_REFLECTION', False),
    }
    config.update(_rag_config_overrides)
    return config


@config_rag_bp.route('/', methods=['GET'])
@role_required('admin')
def get_config():
    return success_response(
        data={'config': get_rag_config()},
        message='Configuracion RAG obtenida exitosamente.'
    )


@config_rag_bp.route('/', methods=['PUT'])
@role_required('admin')
def update_config():
    data = request.get_json()
    allowed_keys = {
        'chunk_size', 'chunk_overlap', 'top_k',
        'score_threshold', 'temperature', 'num_ctx',
        'candidate_multiplier', 'max_chunks_per_doc', 'enable_reflection',
    }

    for key, value in data.items():
        if key not in allowed_keys:
            return error_response(
                f'Parametro no permitido: {key}',
                'Parametro invalido',
                400
            )

    # Validate types
    int_fields = {'chunk_size', 'chunk_overlap', 'top_k', 'num_ctx', 'candidate_multiplier', 'max_chunks_per_doc'}
    float_fields = {'score_threshold', 'temperature'}
    bool_fields = {'enable_reflection'}

    for key, value in data.items():
        if key in int_fields:
            if not isinstance(value, int) or value <= 0:
                return error_response(f'{key} debe ser un entero positivo.', 'Validacion', 400)
        elif key in float_fields:
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                return error_response(f'{key} debe ser un numero entre 0 y 1.', 'Validacion', 400)
        elif key in bool_fields:
            if not isinstance(value, bool):
                return error_response(f'{key} debe ser un booleano (true/false).', 'Validacion', 400)

    _rag_config_overrides.update(data)

    # Also update app config
    for key, value in data.items():
        app_key = f'RAG_{key.upper()}'
        current_app.config[app_key] = value

    return success_response(
        data={'config': get_rag_config()},
        message='Configuracion RAG actualizada exitosamente.'
    )
