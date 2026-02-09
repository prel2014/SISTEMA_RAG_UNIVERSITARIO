from marshmallow import Schema, fields, validate


class FeedbackSchema(Schema):
    id = fields.String(dump_only=True)
    chat_history_id = fields.String(required=True)
    user_id = fields.String(dump_only=True)
    rating = fields.Integer(required=True)
    comment = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class FeedbackCreateSchema(Schema):
    chat_history_id = fields.String(required=True)
    rating = fields.Integer(required=True, validate=validate.OneOf([1, -1]))
    comment = fields.String(allow_none=True)
