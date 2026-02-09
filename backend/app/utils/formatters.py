"""Format database row dicts into API response dicts."""


def format_user(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'email': row['email'],
        'full_name': row['full_name'],
        'role': row['role'],
        'is_active': row['is_active'],
        'created_at': row['created_at'].isoformat() if row.get('created_at') else None,
    }


def format_document(row):
    if not row:
        return None
    doc = {
        'id': row['id'],
        'title': row['title'],
        'original_filename': row['original_filename'],
        'file_type': row['file_type'],
        'file_size': row.get('file_size'),
        'category_id': row.get('category_id'),
        'category': None,
        'uploaded_by': row['uploaded_by'],
        'processing_status': row['processing_status'],
        'processing_error': row.get('processing_error'),
        'chunk_count': row.get('chunk_count', 0),
        'created_at': row['created_at'].isoformat() if row.get('created_at') else None,
    }
    if row.get('category_name'):
        doc['category'] = {
            'id': row['category_id'],
            'name': row['category_name'],
            'slug': row.get('category_slug'),
            'color': row.get('category_color'),
            'icon': row.get('category_icon'),
        }
    return doc


def format_category(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'name': row['name'],
        'slug': row['slug'],
        'description': row.get('description'),
        'icon': row.get('icon'),
        'color': row.get('color'),
        'is_active': row['is_active'],
        'document_count': row.get('document_count', 0),
    }


def format_chat_message(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'conversation_id': row['conversation_id'],
        'user_id': row['user_id'],
        'role': row['role'],
        'content': row['content'],
        'source_documents': row.get('source_documents'),
        'created_at': row['created_at'].isoformat() if row.get('created_at') else None,
    }


def format_feedback(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'chat_history_id': row['chat_history_id'],
        'user_id': row['user_id'],
        'rating': row['rating'],
        'comment': row.get('comment'),
        'created_at': row['created_at'].isoformat() if row.get('created_at') else None,
    }
