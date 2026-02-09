from datetime import datetime, timedelta, timezone
from flask import Blueprint
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.document import Document
from app.models.chat_history import ChatHistory
from app.models.feedback import Feedback
from app.middleware.role_required import role_required
from app.utils.response import success_response

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_documents = Document.query.count()
    total_conversations = db.session.query(
        func.count(func.distinct(ChatHistory.conversation_id))
    ).scalar()
    total_messages = ChatHistory.query.count()

    # Positive feedback percentage
    total_feedback = Feedback.query.count()
    positive_feedback = Feedback.query.filter_by(rating=1).count()
    feedback_rate = round((positive_feedback / total_feedback * 100), 1) if total_feedback > 0 else 0

    return success_response(data={
        'stats': {
            'total_users': total_users,
            'total_documents': total_documents,
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'feedback_rate': feedback_rate,
        }
    })


@analytics_bp.route('/usage', methods=['GET'])
@role_required('admin')
def usage():
    # Messages per day (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    daily_usage = db.session.query(
        func.date(ChatHistory.created_at).label('date'),
        func.count(ChatHistory.id).label('count')
    ).filter(
        ChatHistory.created_at >= thirty_days_ago
    ).group_by(
        func.date(ChatHistory.created_at)
    ).order_by(
        func.date(ChatHistory.created_at)
    ).all()

    return success_response(data={
        'daily_usage': [
            {'date': str(d.date), 'count': d.count} for d in daily_usage
        ]
    })


@analytics_bp.route('/popular-queries', methods=['GET'])
@role_required('admin')
def popular_queries():
    # Most common user questions (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    queries = ChatHistory.query.filter(
        ChatHistory.role == 'user',
        ChatHistory.created_at >= thirty_days_ago
    ).order_by(ChatHistory.created_at.desc()).limit(50).all()

    return success_response(data={
        'popular_queries': [
            {'content': q.content[:200], 'created_at': q.created_at.isoformat()}
            for q in queries
        ]
    })


@analytics_bp.route('/feedback-summary', methods=['GET'])
@role_required('admin')
def feedback_summary():
    total = Feedback.query.count()
    positive = Feedback.query.filter_by(rating=1).count()
    negative = Feedback.query.filter_by(rating=-1).count()

    recent_negative = Feedback.query.filter_by(rating=-1).order_by(
        Feedback.created_at.desc()
    ).limit(10).all()

    return success_response(data={
        'summary': {
            'total': total,
            'positive': positive,
            'negative': negative,
            'rate': round((positive / total * 100), 1) if total > 0 else 0,
        },
        'recent_negative': [f.to_dict() for f in recent_negative]
    })
