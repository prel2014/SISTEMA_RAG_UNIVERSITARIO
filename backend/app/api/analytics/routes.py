from flask import Blueprint
from app.db import call_fn
from app.middleware.role_required import role_required
from app.utils.response import success_response
from app.utils.formatters import format_feedback

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard():
    stats = call_fn('fn_get_dashboard_stats', fetch_one=True)
    return success_response(data={
        'stats': {
            'total_users': stats['total_users'],
            'total_documents': stats['total_documents'],
            'total_conversations': stats['total_conversations'],
            'total_messages': stats['total_messages'],
            'feedback_rate': float(stats['feedback_rate']),
        }
    })


@analytics_bp.route('/usage', methods=['GET'])
@role_required('admin')
def usage():
    rows = call_fn('fn_get_daily_usage', (30,), fetch_all=True)
    return success_response(data={
        'daily_usage': [
            {'date': str(r['date']), 'count': r['count']} for r in rows
        ]
    })


@analytics_bp.route('/popular-queries', methods=['GET'])
@role_required('admin')
def popular_queries():
    rows = call_fn('fn_get_popular_queries', (30, 50), fetch_all=True)
    return success_response(data={
        'popular_queries': [
            {'content': r['content'], 'created_at': r['created_at'].isoformat()}
            for r in rows
        ]
    })


@analytics_bp.route('/feedback-summary', methods=['GET'])
@role_required('admin')
def feedback_summary():
    summary = call_fn('fn_get_feedback_summary', fetch_one=True)
    recent = call_fn('fn_get_recent_negative_feedback', (10,), fetch_all=True)

    return success_response(data={
        'summary': {
            'total': summary['total'],
            'positive': summary['positive'],
            'negative': summary['negative'],
            'rate': float(summary['rate']),
        },
        'recent_negative': [format_feedback(r) for r in recent]
    })
