import uuid
from datetime import datetime, timezone
from app.extensions import db


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(1000), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer)  # bytes
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=True)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    processing_status = db.Column(db.String(20), default='pending')  # pending|processing|completed|failed
    processing_error = db.Column(db.Text)
    chunk_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    chunks = db.relationship('DocumentChunk', backref='document', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'uploaded_by': self.uploaded_by,
            'processing_status': self.processing_status,
            'processing_error': self.processing_error,
            'chunk_count': self.chunk_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
