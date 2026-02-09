from app.extensions import ma
from marshmallow import fields, validate, validates, ValidationError


class UserSchema(ma.Schema):
    id = fields.String(dump_only=True)
    email = fields.Email(required=True)
    full_name = fields.String(required=True)
    role = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class UserCreateSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=255))

    @validates('email')
    def validate_email(self, value):
        if not value.endswith('@upao.edu.pe'):
            raise ValidationError('Solo se permiten correos @upao.edu.pe')


class UserLoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
