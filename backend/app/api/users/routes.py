from flask import Blueprint, request
from app.extensions import db
from app.models.user import User
from app.middleware.role_required import role_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import get_pagination_params

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@role_required('admin')
def list_users():
    page, per_page = get_pagination_params()
    search = request.args.get('search', '')

    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.full_name.ilike(f'%{search}%')
            )
        )

    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return paginated_response(
        items=[u.to_dict() for u in pagination.items],
        total=pagination.total,
        page=page,
        per_page=per_page,
        message='Usuarios obtenidos exitosamente.'
    )


@users_bp.route('/<user_id>', methods=['GET'])
@role_required('admin')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response('Usuario no encontrado.', 'No encontrado', 404)
    return success_response(data={'user': user.to_dict()})


@users_bp.route('/<user_id>/toggle-active', methods=['PUT'])
@role_required('admin')
def toggle_user_active(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response('Usuario no encontrado.', 'No encontrado', 404)
    if user.role == 'admin':
        return error_response('No se puede desactivar al administrador.', 'No permitido', 403)

    user.is_active = not user.is_active
    db.session.commit()

    estado = 'activado' if user.is_active else 'desactivado'
    return success_response(
        data={'user': user.to_dict()},
        message=f'Usuario {estado} exitosamente.'
    )


@users_bp.route('/<user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response('Usuario no encontrado.', 'No encontrado', 404)
    if user.role == 'admin':
        return error_response('No se puede eliminar al administrador.', 'No permitido', 403)

    db.session.delete(user)
    db.session.commit()
    return success_response(message='Usuario eliminado exitosamente.')
