import threading
from flask import Blueprint, request, current_app
from flask_jwt_extended import get_jwt_identity
from app.db import call_fn
from app.middleware.role_required import role_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import get_pagination_params
from app.utils.file_utils import allowed_file, save_upload, get_file_extension, get_file_size, delete_file
from app.utils.formatters import format_document

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/', methods=['GET'])
@role_required('admin')
def list_documents():
    page, per_page = get_pagination_params()
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', '')
    status = request.args.get('status', '')

    rows = call_fn('fn_list_documents', (search, category_id, status, page, per_page), fetch_all=True)

    total = rows[0]['total_count'] if rows else 0
    items = [format_document(r) for r in rows]

    return paginated_response(items, total, page, per_page, 'Documentos obtenidos exitosamente.')


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
    category_id = request.form.get('category_id', '')

    if category_id:
        cat = call_fn('fn_get_category', (category_id,), fetch_one=True)
        if not cat:
            return error_response('Categoria no encontrada.', 'No encontrada', 404)

    file_size = get_file_size(file)
    file_path, unique_name = save_upload(file)
    ext = get_file_extension(file.filename)

    user_id = get_jwt_identity()
    doc = call_fn('fn_create_document', (
        title, file.filename, file_path, ext, file_size, category_id, user_id
    ), fetch_one=True)

    _process_document_async(current_app._get_current_object(), doc['id'])

    return success_response(
        data={'document': format_document(doc)},
        message='Documento subido exitosamente. Procesando...',
        status_code=201
    )


@documents_bp.route('/upload-batch', methods=['POST'])
@role_required('admin')
def upload_batch():
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return error_response('No se enviaron archivos.', 'Archivos requeridos', 400)

    category_id = request.form.get('category_id', '')

    if category_id:
        cat = call_fn('fn_get_category', (category_id,), fetch_one=True)
        if not cat:
            return error_response('Categoria no encontrada.', 'No encontrada', 404)

    user_id = get_jwt_identity()
    app = current_app._get_current_object()

    results = []
    for file in files:
        if file.filename == '':
            continue

        if not allowed_file(file.filename):
            results.append({
                'success': False,
                'filename': file.filename,
                'error': 'Tipo de archivo no permitido.',
            })
            continue

        try:
            title = file.filename.rsplit('.', 1)[0]
            file_size = get_file_size(file)
            file_path, unique_name = save_upload(file)
            ext = get_file_extension(file.filename)

            doc = call_fn('fn_create_document', (
                title, file.filename, file_path, ext, file_size, category_id, user_id
            ), fetch_one=True)

            _process_document_async(app, doc['id'])

            results.append({
                'success': True,
                'filename': file.filename,
                'document': format_document(doc),
            })
        except Exception as e:
            results.append({
                'success': False,
                'filename': file.filename,
                'error': str(e),
            })

    total = len(results)
    successful = sum(1 for r in results if r['success'])

    status_code = 201 if successful == total else (207 if successful > 0 else 400)

    return success_response(
        data={'results': results, 'total': total, 'successful': successful},
        message=f'{successful} de {total} archivo(s) subido(s) exitosamente.',
        status_code=status_code
    )


def _process_document_async(app, document_id):
    def process():
        with app.app_context():
            from app.rag.pipeline import process_document
            try:
                process_document(document_id, app=app)
            except Exception as e:
                # process_document ya actualizó el status a 'failed'
                print(f"[Pipeline error] {document_id}: {e}")

    thread = threading.Thread(target=process)
    thread.daemon = True
    thread.start()


@documents_bp.route('/<doc_id>', methods=['GET'])
@role_required('admin')
def get_document(doc_id):
    doc = call_fn('fn_get_document', (doc_id,), fetch_one=True)
    if not doc:
        return error_response('Documento no encontrado.', 'No encontrado', 404)
    return success_response(data={'document': format_document(doc)})


@documents_bp.route('/<doc_id>', methods=['PUT'])
@role_required('admin')
def update_document(doc_id):
    doc = call_fn('fn_get_document', (doc_id,), fetch_one=True)
    if not doc:
        return error_response('Documento no encontrado.', 'No encontrado', 404)

    data = request.get_json()
    title = data.get('title')
    category_id = data.get('category_id')

    if category_id is not None and category_id:
        cat = call_fn('fn_get_category', (category_id,), fetch_one=True)
        if not cat:
            return error_response('Categoria no encontrada.', 'No encontrada', 404)

    updated = call_fn('fn_update_document', (doc_id, title, category_id), fetch_one=True)
    return success_response(
        data={'document': format_document(updated)},
        message='Documento actualizado exitosamente.'
    )


@documents_bp.route('/<doc_id>', methods=['DELETE'])
@role_required('admin')
def delete_document(doc_id):
    doc = call_fn('fn_get_document', (doc_id,), fetch_one=True)
    if not doc:
        return error_response('Documento no encontrado.', 'No encontrado', 404)

    # Los chunks se eliminan vía ON DELETE CASCADE en document_chunks
    file_path = call_fn('fn_delete_document', (doc_id,), fetch_one=True)
    if file_path:
        delete_file(file_path['fn_delete_document'])

    return success_response(message='Documento eliminado exitosamente.')


@documents_bp.route('/<doc_id>/reprocess', methods=['POST'])
@role_required('admin')
def reprocess_document(doc_id):
    doc = call_fn('fn_get_document', (doc_id,), fetch_one=True)
    if not doc:
        return error_response('Documento no encontrado.', 'No encontrado', 404)

    # fn_reset_document_for_reprocess elimina chunks existentes vía DELETE
    call_fn('fn_reset_document_for_reprocess', (doc_id,), fetch_one=True)

    doc = call_fn('fn_get_document', (doc_id,), fetch_one=True)

    _process_document_async(current_app._get_current_object(), doc_id)

    return success_response(
        data={'document': format_document(doc)},
        message='Reprocesamiento iniciado.'
    )
