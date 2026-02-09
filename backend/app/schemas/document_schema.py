from marshmallow import Schema, fields


class DocumentSchema(Schema):
    id = fields.String(dump_only=True)
    title = fields.String(required=True)
    original_filename = fields.String(dump_only=True)
    file_type = fields.String(dump_only=True)
    file_size = fields.Integer(dump_only=True)
    category_id = fields.String(allow_none=True)
    category = fields.Dict(dump_only=True)
    uploaded_by = fields.String(dump_only=True)
    processing_status = fields.String(dump_only=True)
    processing_error = fields.String(dump_only=True)
    chunk_count = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
