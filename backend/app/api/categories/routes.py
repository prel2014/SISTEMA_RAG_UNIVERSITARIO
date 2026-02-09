import re
from flask import Blueprint, request
from marshmallow import ValidationError
from app.extensions import db
from app.models.category import Category
from app.schemas.category_schema import CategoryCreateSchema
from app.middleware.role_required import role_required
from app.middleware.auth_middleware import auth_required
from app.utils.response import success_response, error_response

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
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    return success_response(
        data={'categories': [c.to_dict() for c in categories]},
        message='Categorias obtenidas exitosamente.'
    )


@categories_bp.route('/all', methods=['GET'])
@role_required('admin')
def list_all_categories():
    categories = Category.query.order_by(Category.name).all()
    return success_response(
        data={'categories': [c.to_dict() for c in categories]},
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
    if Category.query.filter_by(slug=slug).first():
        return error_response('Ya existe una categoria con ese nombre.', 'Duplicado', 409)

    category = Category(
        name=data['name'],
        slug=slug,
        description=data.get('description'),
        icon=data.get('icon', 'folder'),
        color=data.get('color', '#1E3A5F'),
    )
    db.session.add(category)
    db.session.commit()

    return success_response(
        data={'category': category.to_dict()},
        message='Categoria creada exitosamente.',
        status_code=201
    )


@categories_bp.route('/<cat_id>', methods=['PUT'])
@role_required('admin')
def update_category(cat_id):
    category = Category.query.get(cat_id)
    if not category:
        return error_response('Categoria no encontrada.', 'No encontrada', 404)

    data = request.get_json()
    if 'name' in data:
        slug = slugify(data['name'])
        existing = Category.query.filter(Category.slug == slug, Category.id != cat_id).first()
        if existing:
            return error_response('Ya existe una categoria con ese nombre.', 'Duplicado', 409)
        category.name = data['name']
        category.slug = slug
    if 'description' in data:
        category.description = data['description']
    if 'icon' in data:
        category.icon = data['icon']
    if 'color' in data:
        category.color = data['color']
    if 'is_active' in data:
        category.is_active = data['is_active']

    db.session.commit()
    return success_response(
        data={'category': category.to_dict()},
        message='Categoria actualizada exitosamente.'
    )


@categories_bp.route('/<cat_id>', methods=['DELETE'])
@role_required('admin')
def delete_category(cat_id):
    category = Category.query.get(cat_id)
    if not category:
        return error_response('Categoria no encontrada.', 'No encontrada', 404)

    if category.documents.count() > 0:
        return error_response(
            'No se puede eliminar una categoria con documentos asociados.',
            'No permitido',
            409
        )

    db.session.delete(category)
    db.session.commit()
    return success_response(message='Categoria eliminada exitosamente.')
