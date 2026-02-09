import threading
from flask import Blueprint, request, current_app
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models.document import Document
from app.models.category import Category
from app.models.chunk import DocumentChunk
from app.middleware.role_required import role_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import get_pagination_params
from app.utils.file_utils import allowed_file, save_upload, get_file_extension, get_file_size, delete_file

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/', methods=['GET'])
@role_required('admin')
def list_documents():
    page, per_page = get_pagination_params()
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', '')
    status = request.args.get('status', '')

    query = Document.query
    if search:
        query = query.filter(
            db.or_(
                Document.title.ilike(f'%{search}%'),
                Document.original_filename.ilike(f'%{search}%')
            )
        )
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(processing_status=status)

    query = query.order_by(Document.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return paginated_response(
        items=[d.to_dict() for d in pagination.items],
        total=pagination.total,
        page=page,
        per_page=per_page,
        message='Documentos obtenidos exitosamente.'
    )


@documents_bp.route('/upload', methods=['POST'])
@role_required('admin')
def upload_document():
    if 'file' not in request.files:
        return error_response('No se envio ningun archivo.', 'Archivo requerido', 400)

    file = request.files['file']
    if file.filename == '':
        return error_response('Nombre de archivo vacio.', 'Archivo invalido', 400)

    if not allowed_file(file.filename):
        return error_response(
            'Tipo de archivo no permitido. Formatos aceptados: PDF, DOCX, XLSX, TXT, PNG, JPG.',
            'Tipo no permitido',
            400
        )

    title = request.form.get('title', file.filename)
    category_id = request.form.get('category_id')

    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return error_response('Categoria no encontrada.', 'No encontrada', 404)

    file_size = get_file_size(file)
    file_path, unique_name = save_upload(file)
    ext = get_file_extension(file.filename)

    user_id = get_jwt_identity()
    document = Document(
        title=title,
        original_filename=file.filename,
        file_path=file_path,
        file_type=ext,
        file_size=file_size,
        category_id=category_id,
        uploaded_by=user_id,
        processing_status='pending'
    )
    db.session.add(document)
    db.session.commit()

    # Process document in background
    _process_document_async(current_app._get_current_object(), document.id)

    return success_response(
        data={'document': document.to_dict()},
        message='Documento subido exitosamente. Procesando...',
        status_code=201
    )


def _process_document_async(app, document_id):
    def process():
        with app.app_context():
            from app.rag.pipeline import process_document
            try:
                process_document(document_id)
            except Exception as e:
                doc = Document.query.get(document_id)
                if doc:
                    doc.processing_status = 'failed'
                    doc.processing_error = str(e)
                    db.session.commit()

    thread = threading.Thread(target=process)
    thread.daemon = True
    thread.start()


@documents_bp.route('/<doc_id>', methods=['GET'])
@role_required('admin')
def get_document(doc_id):
    document = Document.query.get(doc_id)
    if not document:
        return error_response('Documento no encontrado.', 'No encontrado', 404)
    return success_response(data={'document': document.to_dict()})


@documents_bp.route('/<doc_id>', methods=['PUT'])
@role_required('admin')
def update_document(doc_id):
    document = Document.query.get(doc_id)
    if not document:
        return error_response('Documento no encontrado.', 'No encontrado', 404)

    data = request.get_json()
    if 'title' in data:
        document.title = data['title']
    if 'category_id' in data:
        if data['category_id']:
            category = Category.query.get(data['category_id'])
            if not category:
                return error_response('Categoria no encontrada.', 'No encontrada', 404)
        document.category_id = data['category_id']

    db.session.commit()
    return success_response(
        data={'document': document.to_dict()},
        message='Documento actualizado exitosamente.'
    )


@documents_bp.route('/<doc_id>', methods=['DELETE'])
@role_required('admin')
def delete_document(doc_id):
    document = Document.query.get(doc_id)
    if not document:
        return error_response('Documento no encontrado.', 'No encontrado', 404)

    # Delete from Qdrant
    try:
        from app.rag.vector_store import delete_document_vectors
        delete_document_vectors(doc_id)
    except Exception:
        pass

    # Delete file
    delete_file(document.file_path)

    # Update category count
    if document.category_id:
        category = Category.query.get(document.category_id)
        if category and category.document_count > 0:
            category.document_count -= 1

    db.session.delete(document)
    db.session.commit()
    return success_response(message='Documento eliminado exitosamente.')


@documents_bp.route('/<doc_id>/reprocess', methods=['POST'])
@role_required('admin')
def reprocess_document(doc_id):
    document = Document.query.get(doc_id)
    if not document:
        return error_response('Documento no encontrado.', 'No encontrado', 404)

    # Delete existing chunks and vectors
    try:
        from app.rag.vector_store import delete_document_vectors
        delete_document_vectors(doc_id)
    except Exception:
        pass

    DocumentChunk.query.filter_by(document_id=doc_id).delete()
    document.processing_status = 'pending'
    document.processing_error = None
    document.chunk_count = 0
    db.session.commit()

    _process_document_async(current_app._get_current_object(), doc_id)

    return success_response(
        data={'document': document.to_dict()},
        message='Reprocesamiento iniciado.'
    )
