import uuid
import json
from flask import Blueprint, request, Response, stream_with_context
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.models.chat_history import ChatHistory
from app.models.feedback import Feedback
from app.schemas.chat_schema import ChatMessageSchema
from app.schemas.feedback_schema import FeedbackCreateSchema
from app.middleware.auth_middleware import auth_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import get_pagination_params

chat_bp = Blueprint('chat', __name__)
message_schema = ChatMessageSchema()
feedback_create_schema = FeedbackCreateSchema()


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
    user_msg = ChatHistory(
        conversation_id=conversation_id,
        user_id=user_id,
        role='user',
        content=data['message']
    )
    db.session.add(user_msg)
    db.session.commit()

    # Get RAG response
    try:
        from app.rag.chain import get_rag_response
        result = get_rag_response(data['message'], category_id=category_id)

        # Save assistant message
        assistant_msg = ChatHistory(
            conversation_id=conversation_id,
            user_id=user_id,
            role='assistant',
            content=result['answer'],
            source_documents=result.get('sources', [])
        )
        db.session.add(assistant_msg)
        db.session.commit()

        return success_response(
            data={
                'message': assistant_msg.to_dict(),
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
    user_msg = ChatHistory(
        conversation_id=conversation_id,
        user_id=user_id,
        role='user',
        content=data['message']
    )
    db.session.add(user_msg)
    db.session.commit()

    def generate():
        full_response = ''
        sources = []
        try:
            from app.rag.chain import get_rag_response_stream
            for chunk in get_rag_response_stream(data['message'], category_id=category_id):
                if chunk.get('type') == 'token':
                    full_response += chunk['content']
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk['content']})}\n\n"
                elif chunk.get('type') == 'sources':
                    sources = chunk['sources']
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

            # Save assistant message
            assistant_msg = ChatHistory(
                conversation_id=conversation_id,
                user_id=user_id,
                role='assistant',
                content=full_response,
                source_documents=sources
            )
            db.session.add(assistant_msg)
            db.session.commit()

            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id, 'message_id': assistant_msg.id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

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

    # Get distinct conversations with latest message
    subquery = db.session.query(
        ChatHistory.conversation_id,
        db.func.max(ChatHistory.created_at).label('last_message_at'),
        db.func.min(ChatHistory.content).label('first_message'),
    ).filter_by(
        user_id=user_id, role='user'
    ).group_by(
        ChatHistory.conversation_id
    ).subquery()

    total = db.session.query(subquery).count()
    conversations = db.session.query(subquery).order_by(
        subquery.c.last_message_at.desc()
    ).offset((page - 1) * per_page).limit(per_page).all()

    items = [{
        'conversation_id': c.conversation_id,
        'last_message_at': c.last_message_at.isoformat() if c.last_message_at else None,
        'preview': c.first_message[:100] if c.first_message else '',
    } for c in conversations]

    return paginated_response(items, total, page, per_page, 'Conversaciones obtenidas.')


@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
@auth_required
def get_conversation(conversation_id):
    user_id = get_jwt_identity()
    messages = ChatHistory.query.filter_by(
        conversation_id=conversation_id, user_id=user_id
    ).order_by(ChatHistory.created_at).all()

    if not messages:
        return error_response('Conversacion no encontrada.', 'No encontrada', 404)

    return success_response(
        data={'messages': [m.to_dict() for m in messages]},
        message='Conversacion obtenida exitosamente.'
    )


@chat_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@auth_required
def delete_conversation(conversation_id):
    user_id = get_jwt_identity()
    messages = ChatHistory.query.filter_by(
        conversation_id=conversation_id, user_id=user_id
    ).all()

    if not messages:
        return error_response('Conversacion no encontrada.', 'No encontrada', 404)

    for msg in messages:
        db.session.delete(msg)
    db.session.commit()

    return success_response(message='Conversacion eliminada exitosamente.')


@chat_bp.route('/feedback', methods=['POST'])
@auth_required
def submit_feedback():
    try:
        data = feedback_create_schema.load(request.get_json())
    except ValidationError as err:
        return error_response(str(err.messages), 'Error de validacion', 400)

    user_id = get_jwt_identity()
    chat_msg = ChatHistory.query.get(data['chat_history_id'])
    if not chat_msg:
        return error_response('Mensaje no encontrado.', 'No encontrado', 404)

    existing = Feedback.query.filter_by(
        chat_history_id=data['chat_history_id'], user_id=user_id
    ).first()
    if existing:
        existing.rating = data['rating']
        existing.comment = data.get('comment')
    else:
        feedback = Feedback(
            chat_history_id=data['chat_history_id'],
            user_id=user_id,
            rating=data['rating'],
            comment=data.get('comment')
        )
        db.session.add(feedback)

    db.session.commit()
    return success_response(message='Valoracion enviada exitosamente.')
