from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.db import call_fn


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = call_fn('fn_get_user_by_id', (user_id,), fetch_one=True)

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
                    'message': 'Su cuenta ha sido desactivada.'
                }), 403

            if user['role'] != role:
                return jsonify({
                    'success': False,
                    'error': 'Acceso denegado',
                    'message': f'Se requiere rol de {role} para acceder a este recurso.'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
