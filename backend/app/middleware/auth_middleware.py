from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps
from app.db import call_fn


def register_jwt_callbacks(jwt):
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': 'Token expirado',
            'message': 'Su sesion ha expirado. Por favor inicie sesion nuevamente.'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'error': 'Token invalido',
            'message': 'Token de acceso invalido.'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'error': 'Token requerido',
            'message': 'Se requiere un token de acceso.'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': 'Token revocado',
            'message': 'El token ha sido revocado.'
        }), 401


def get_current_user():
    user_id = get_jwt_identity()
    return call_fn('fn_get_user_by_id', (user_id,), fetch_one=True)


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'message': 'El usuario asociado al token no existe.'
            }), 401
        if not user['is_active']:
            return jsonify({
                'success': False,
                'error': 'Cuenta desactivada',
                'message': 'Su cuenta ha sido desactivada. Contacte al administrador.'
            }), 403
        return fn(*args, **kwargs)
    return wrapper
