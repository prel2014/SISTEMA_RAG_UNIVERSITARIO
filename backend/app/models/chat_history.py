import uuid
from datetime import datetime, timezone
from app.extensions import db


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user | assistant
    content = db.Column(db.Text, nullable=False)
    source_documents = db.Column(db.JSON)  # [{title, page, chunk_preview}]
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    feedbacks = db.relationship('Feedback', backref='chat_message', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'role': self.role,
            'content': self.content,
            'source_documents': self.source_documents,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
