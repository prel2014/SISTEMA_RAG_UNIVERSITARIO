from flask import Blueprint, request
from app.db import call_fn
from app.middleware.role_required import role_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import get_pagination_params
from app.utils.formatters import format_user

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@role_required('admin')
def list_users():
    page, per_page = get_pagination_params()
    search = request.args.get('search', '')

    rows = call_fn('fn_list_users', (search, page, per_page), fetch_all=True)

    total = rows[0]['total_count'] if rows else 0
    items = [format_user(r) for r in rows]

    return paginated_response(items, total, page, per_page, 'Usuarios obtenidos exitosamente.')


@users_bp.route('/<user_id>', methods=['GET'])
@role_required('admin')
def get_user(user_id):
    user = call_fn('fn_get_user_by_id', (user_id,), fetch_one=True)
    if not user:
        return error_response('Usuario no encontrado.', 'No encontrado', 404)
    return success_response(data={'user': format_user(user)})


@users_bp.route('/<user_id>/toggle-active', methods=['PUT'])
@role_required('admin')
def toggle_user_active(user_id):
    user = call_fn('fn_get_user_by_id', (user_id,), fetch_one=True)
    if not user:
        return error_response('Usuario no encontrado.', 'No encontrado', 404)
    if user['role'] == 'admin':
        return error_response('No se puede desactivar al administrador.', 'No permitido', 403)

    updated = call_fn('fn_toggle_user_active', (user_id,), fetch_one=True)
    estado = 'activado' if updated['is_active'] else 'desactivado'
    return success_response(
        data={'user': format_user(updated)},
        message=f'Usuario {estado} exitosamente.'
    )


@users_bp.route('/<user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    user = call_fn('fn_get_user_by_id', (user_id,), fetch_one=True)
    if not user:
        return error_response('Usuario no encontrado.', 'No encontrado', 404)
    if user['role'] == 'admin':
        return error_response('No se puede eliminar al administrador.', 'No permitido', 403)

    call_fn('fn_delete_user', (user_id,), fetch_one=True)
    return success_response(message='Usuario eliminado exitosamente.')
