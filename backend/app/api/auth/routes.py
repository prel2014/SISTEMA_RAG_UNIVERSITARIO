from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import call_fn
from app.schemas.user_schema import UserCreateSchema, UserLoginSchema
from app.utils.response import success_response, error_response
from app.utils.formatters import format_user
from app.middleware.auth_middleware import auth_required, get_current_user

auth_bp = Blueprint('auth', __name__)

user_create_schema = UserCreateSchema()
user_login_schema = UserLoginSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = user_create_schema.load(request.get_json())
    except ValidationError as err:
        return error_response(
            message=str(err.messages),
            error='Error de validacion',
            status_code=400
        )

    existing = call_fn('fn_get_user_by_email', (data['email'],), fetch_one=True)
    if existing:
        return error_response(
            message='Ya existe una cuenta con este correo electronico.',
            error='Email duplicado',
            status_code=409
        )

    password_hash = generate_password_hash(data['password'])
    user = call_fn('fn_create_user', (data['email'], password_hash, data['full_name'], 'user'), fetch_one=True)

    access_token = create_access_token(identity=user['id'])
    refresh_token = create_refresh_token(identity=user['id'])

    return success_response(
        data={
            'user': format_user(user),
            'access_token': access_token,
            'refresh_token': refresh_token,
        },
        message='Registro exitoso. Bienvenido a UPAO RAG.',
        status_code=201
    )


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = user_login_schema.load(request.get_json())
    except ValidationError as err:
        return error_response(
            message=str(err.messages),
            error='Error de validacion',
            status_code=400
        )

    user = call_fn('fn_get_user_by_email', (data['email'],), fetch_one=True)

    if not user or not check_password_hash(user['password_hash'], data['password']):
        return error_response(
            message='Correo electronico o contrasena incorrectos.',
            error='Credenciales invalidas',
            status_code=401
        )

    if not user['is_active']:
        return error_response(
            message='Su cuenta ha sido desactivada. Contacte al administrador.',
            error='Cuenta desactivada',
            status_code=403
        )

    access_token = create_access_token(identity=user['id'])
    refresh_token = create_refresh_token(identity=user['id'])

    return success_response(
        data={
            'user': format_user(user),
            'access_token': access_token,
            'refresh_token': refresh_token,
        },
        message='Inicio de sesion exitoso.'
    )


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = call_fn('fn_get_user_by_id', (user_id,), fetch_one=True)

    if not user or not user['is_active']:
        return error_response(
            message='No se pudo renovar el token.',
            error='Token invalido',
            status_code=401
        )

    access_token = create_access_token(identity=user_id)
    return success_response(
        data={'access_token': access_token},
        message='Token renovado exitosamente.'
    )


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return success_response(message='Sesion cerrada exitosamente.')


@auth_bp.route('/me', methods=['GET'])
@auth_required
def me():
    user = get_current_user()
    return success_response(
        data={'user': format_user(user)},
        message='Perfil obtenido exitosamente.'
    )
