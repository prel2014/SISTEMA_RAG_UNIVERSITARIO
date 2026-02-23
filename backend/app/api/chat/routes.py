import uuid
import json
from flask import Blueprint, request, Response, stream_with_context
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from psycopg2.extras import Json
from app.db import call_fn
from app.schemas.chat_schema import ChatMessageSchema
from app.schemas.feedback_schema import FeedbackCreateSchema
from app.middleware.auth_middleware import auth_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import get_pagination_params
from app.utils.formatters import format_chat_message

chat_bp = Blueprint('chat', __name__)
message_schema = ChatMessageSchema()
feedback_create_schema = FeedbackCreateSchema()


def _get_recent_history(conversation_id, user_id, limit=6):
    rows = call_fn('fn_get_conversation_messages', (conversation_id, user_id), fetch_all=True) or []
    return [{'role': r['role'], 'content': r['content']} for r in rows[-limit:]]


@chat_bp.route('/message', methods=['POST'])
@auth_required
def send_message():
    try:
        data = message_schema.load(request.get_json())
    except ValidationError as err:
        return error_response(str(err.messages), 'Error de validacion', 400)

    user_id = get_jwt_identity()
    conversation_id = data.get('conversation_id') or str(uuid.uuid4())
    category_id = data.get('category_id')

    # Save user message
    call_fn('fn_create_chat_message', (conversation_id, user_id, 'user', data['message'], None), fetch_one=True)

    # Get recent history (before saving current message it was already saved above)
    conversation_history = _get_recent_history(conversation_id, user_id)

    try:
        from app.rag.chain import get_rag_response
        result = get_rag_response(data['message'], category_id=category_id,
                                  conversation_history=conversation_history)

        sources = result.get('sources', [])
        assistant_msg = call_fn('fn_create_chat_message', (
            conversation_id, user_id, 'assistant', result['answer'], Json(sources)
        ), fetch_one=True)

        return success_response(
            data={
                'message': format_chat_message(assistant_msg),
                'conversation_id': conversation_id,
            },
            message='Respuesta generada exitosamente.'
        )
    except Exception as e:
        return error_response(
            f'Error al generar respuesta: {str(e)}',
            'Error RAG',
            500
        )


@chat_bp.route('/stream', methods=['POST'])
@auth_required
def stream_message():
    try:
        data = message_schema.load(request.get_json())
    except ValidationError as err:
        return error_response(str(err.messages), 'Error de validacion', 400)

    user_id = get_jwt_identity()
    conversation_id = data.get('conversation_id') or str(uuid.uuid4())
    category_id = data.get('category_id')

    # Save user message
    call_fn('fn_create_chat_message', (conversation_id, user_id, 'user', data['message'], None), fetch_one=True)

    # Get recent history for context
    conversation_history = _get_recent_history(conversation_id, user_id)

    def generate():
        full_response = ''
        sources = []
        try:
            from app.rag.chain import get_rag_response_stream
            for chunk in get_rag_response_stream(data['message'], category_id=category_id,
                                                  conversation_history=conversation_history):
                if chunk.get('type') == 'token':
                    full_response += chunk['content']
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk['content']})}\n\n"
                elif chunk.get('type') == 'sources':
                    sources = chunk['sources']
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

            assistant_msg = call_fn('fn_create_chat_message', (
                conversation_id, user_id, 'assistant', full_response, Json(sources) if sources else None
            ), fetch_one=True)

            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id, 'message_id': assistant_msg['id']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id, 'message_id': None})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )


@chat_bp.route('/conversations', methods=['GET'])
@auth_required
def list_conversations():
    user_id = get_jwt_identity()
    page, per_page = get_pagination_params()

    rows = call_fn('fn_list_conversations', (user_id, page, per_page), fetch_all=True)

    total = rows[0]['total_count'] if rows else 0
    items = [{
        'conversation_id': r['conversation_id'],
        'last_message_at': r['last_message_at'].isoformat() if r['last_message_at'] else None,
        'preview': r['preview'] or '',
    } for r in rows]

    return paginated_response(items, total, page, per_page, 'Conversaciones obtenidas.')


@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
@auth_required
def get_conversation(conversation_id):
    user_id = get_jwt_identity()
    rows = call_fn('fn_get_conversation_messages', (conversation_id, user_id), fetch_all=True)

    if not rows:
        return error_response('Conversacion no encontrada.', 'No encontrada', 404)

    return success_response(
        data={'messages': [format_chat_message(r) for r in rows]},
        message='Conversacion obtenida exitosamente.'
    )


@chat_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@auth_required
def delete_conversation(conversation_id):
    user_id = get_jwt_identity()
    result = call_fn('fn_delete_conversation', (conversation_id, user_id), fetch_one=True)

    if not result or result['fn_delete_conversation'] == 0:
        return error_response('Conversacion no encontrada.', 'No encontrada', 404)

    return success_response(message='Conversacion eliminada exitosamente.')


@chat_bp.route('/feedback', methods=['POST'])
@auth_required
def submit_feedback():
    try:
        data = feedback_create_schema.load(request.get_json())
    except ValidationError as err:
        return error_response(str(err.messages), 'Error de validacion', 400)

    user_id = get_jwt_identity()

    from app.db import execute
    msg = execute(
        'SELECT id FROM chat_history WHERE id = %s',
        (data['chat_history_id'],),
        fetch_one=True
    )
    if not msg:
        return error_response('Mensaje no encontrado.', 'No encontrado', 404)

    call_fn('fn_upsert_feedback', (
        data['chat_history_id'], user_id, data['rating'], data.get('comment')
    ), fetch_one=True)

    return success_response(message='Valoracion enviada exitosamente.')


_FALLBACK_SUGGESTIONS = [
    'Cuales son los requisitos de admision?',
    'Como solicito una beca?',
    'Cual es el calendario academico?',
    'Donde encuentro los silabos?',
    'Como realizo un tramite academico?',
    'Cuales son los servicios de bienestar?',
]


@chat_bp.route('/autocomplete', methods=['GET'])
@auth_required
def autocomplete():
    query = request.args.get('q', '').strip()
    if len(query) < 3:
        return success_response(data={'suggestions': []}, message='Sugerencias obtenidas.')
    rows = call_fn('fn_autocomplete_chat', (query, 3), fetch_all=True) or []
    suggestions = [{'text': r['suggestion'], 'source': r['source']} for r in rows]
    return success_response(data={'suggestions': suggestions}, message='Sugerencias obtenidas.')


@chat_bp.route('/suggested-questions', methods=['GET'])
@auth_required
def suggested_questions():
    rows = call_fn('fn_get_frequent_questions', (2, 6), fetch_all=True) or []
    questions = [r['question'] for r in rows]
    if len(questions) < 3:
        existing_lower = {q.lower() for q in questions}
        for fallback in _FALLBACK_SUGGESTIONS:
            if len(questions) >= 6:
                break
            if fallback.lower() not in existing_lower:
                questions.append(fallback)
                existing_lower.add(fallback.lower())
    return success_response(
        data={'questions': questions[:6]},
        message='Preguntas sugeridas obtenidas.'
    )
