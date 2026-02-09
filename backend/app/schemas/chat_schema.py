from marshmallow import Schema, fields, validate


class ChatMessageSchema(Schema):
    message = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    conversation_id = fields.String(allow_none=True)
    category_id = fields.String(allow_none=True)


class ChatHistorySchema(Schema):
    id = fields.String(dump_only=True)
    conversation_id = fields.String(dump_only=True)
    user_id = fields.String(dump_only=True)
    role = fields.String(dump_only=True)
    content = fields.String(dump_only=True)
    source_documents = fields.List(fields.Dict(), dump_only=True)
    created_at = fields.DateTime(dump_only=True)
