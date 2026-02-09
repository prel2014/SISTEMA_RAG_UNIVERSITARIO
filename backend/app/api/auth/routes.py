from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from marshmallow import ValidationError
from app.extensions import db
from app.models.user import User
from app.schemas.user_schema import UserCreateSchema, UserLoginSchema, UserSchema
from app.utils.response import success_response, error_response
from app.middleware.auth_middleware import auth_required, get_current_user

auth_bp = Blueprint('auth', __name__)

user_create_schema = UserCreateSchema()
user_login_schema = UserLoginSchema()
user_schema = UserSchema()


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

    if User.query.filter_by(email=data['email']).first():
        return error_response(
            message='Ya existe una cuenta con este correo electronico.',
            error='Email duplicado',
            status_code=409
        )

    user = User(
        email=data['email'],
        full_name=data['full_name'],
        role='user'
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return success_response(
        data={
            'user': user.to_dict(),
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

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return error_response(
            message='Correo electronico o contrasena incorrectos.',
            error='Credenciales invalidas',
            status_code=401
        )

    if not user.is_active:
        return error_response(
            message='Su cuenta ha sido desactivada. Contacte al administrador.',
            error='Cuenta desactivada',
            status_code=403
        )

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return success_response(
        data={
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
        },
        message='Inicio de sesion exitoso.'
    )


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_active:
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
        data={'user': user.to_dict()},
        message='Perfil obtenido exitosamente.'
    )
