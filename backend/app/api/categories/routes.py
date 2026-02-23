import re
from flask import Blueprint, request
from marshmallow import ValidationError
from app.db import call_fn
from app.schemas.category_schema import CategoryCreateSchema
from app.middleware.role_required import role_required
from app.middleware.auth_middleware import auth_required
from app.utils.response import success_response, error_response
from app.utils.formatters import format_category

categories_bp = Blueprint('categories', __name__)
category_create_schema = CategoryCreateSchema()


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[áàäâ]', 'a', text)
    text = re.sub(r'[éèëê]', 'e', text)
    text = re.sub(r'[íìïî]', 'i', text)
    text = re.sub(r'[óòöô]', 'o', text)
    text = re.sub(r'[úùüû]', 'u', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


@categories_bp.route('/', methods=['GET'])
@auth_required
def list_categories():
    rows = call_fn('fn_list_categories', (True,), fetch_all=True)
    return success_response(
        data={'categories': [format_category(r) for r in rows]},
        message='Categorias obtenidas exitosamente.'
    )


@categories_bp.route('/all', methods=['GET'])
@role_required('admin')
def list_all_categories():
    rows = call_fn('fn_list_categories', (False,), fetch_all=True)
    return success_response(
        data={'categories': [format_category(r) for r in rows]},
        message='Categorias obtenidas exitosamente.'
    )


@categories_bp.route('/', methods=['POST'])
@role_required('admin')
def create_category():
    try:
        data = category_create_schema.load(request.get_json())
    except ValidationError as err:
        return error_response(str(err.messages), 'Error de validacion', 400)

    slug = slugify(data['name'])
    exists = call_fn('fn_category_slug_exists', (slug,), fetch_one=True)
    if exists and exists['fn_category_slug_exists']:
        return error_response('Ya existe una categoria con ese nombre.', 'Duplicado', 409)

    row = call_fn('fn_create_category', (
        data['name'], slug, data.get('description'),
        data.get('icon', 'folder'), data.get('color', '#1E3A5F')
    ), fetch_one=True)

    return success_response(
        data={'category': format_category(row)},
        message='Categoria creada exitosamente.',
        status_code=201
    )


@categories_bp.route('/<cat_id>', methods=['PUT'])
@role_required('admin')
def update_category(cat_id):
    cat = call_fn('fn_get_category', (cat_id,), fetch_one=True)
    if not cat:
        return error_response('Categoria no encontrada.', 'No encontrada', 404)

    data = request.get_json()
    slug = None
    name = None
    if 'name' in data:
        slug = slugify(data['name'])
        exists = call_fn('fn_category_slug_exists', (slug, cat_id), fetch_one=True)
        if exists and exists['fn_category_slug_exists']:
            return error_response('Ya existe una categoria con ese nombre.', 'Duplicado', 409)
        name = data['name']

    row = call_fn('fn_update_category', (
        cat_id, name, slug,
        data.get('description'), data.get('icon'), data.get('color'),
        data.get('is_active'), data.get('exclude_from_rag')
    ), fetch_one=True)

    return success_response(
        data={'category': format_category(row)},
        message='Categoria actualizada exitosamente.'
    )


@categories_bp.route('/<cat_id>', methods=['DELETE'])
@role_required('admin')
def delete_category(cat_id):
    cat = call_fn('fn_get_category', (cat_id,), fetch_one=True)
    if not cat:
        return error_response('Categoria no encontrada.', 'No encontrada', 404)

    deleted = call_fn('fn_delete_category', (cat_id,), fetch_one=True)
    if not deleted or not deleted['fn_delete_category']:
        return error_response(
            'No se puede eliminar una categoria con documentos asociados.',
            'No permitido',
            409
        )

    return success_response(message='Categoria eliminada exitosamente.')
