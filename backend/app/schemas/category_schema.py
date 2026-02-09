from marshmallow import Schema, fields, validate


class CategorySchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True)
    slug = fields.String(dump_only=True)
    description = fields.String(allow_none=True)
    icon = fields.String()
    color = fields.String()
    is_active = fields.Boolean()
    document_count = fields.Integer(dump_only=True)


class CategoryCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    description = fields.String(allow_none=True)
    icon = fields.String(load_default='folder')
    color = fields.String(load_default='#1E3A5F')
