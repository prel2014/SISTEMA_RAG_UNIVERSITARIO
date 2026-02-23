import threading
from flask import Blueprint, request, current_app
from flask_jwt_extended import get_jwt_identity
from app.db import call_fn
from app.middleware.role_required import role_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import get_pagination_params
from app.utils.file_utils import save_upload, get_file_extension, get_file_size, delete_file
from app.utils.formatters import format_thesis_check

originality_bp = Blueprint('originality', __name__)

ALLOWED_TYPES = {'pdf', 'docx', 'txt'}


def _allowed_thesis_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_TYPES


@originality_bp.route('/', methods=['POST'])
@role_required('admin')
def submit_check():
    if 'file' not in request.files:
        return error_response('No se envio ningun archivo.', 'Archivo requerido', 400)

    file = request.files['file']
    if file.filename == '':
        return error_response('Nombre de archivo vacio.', 'Archivo invalido', 400)

    if not _allowed_thesis_file(file.filename):
        return error_response(
            'Tipo de archivo no permitido. Formatos aceptados: PDF, DOCX, TXT.',
            'Tipo no permitido',
            400
        )

    threshold_str = request.form.get('score_threshold', '')
    try:
        threshold = float(threshold_str) if threshold_str else current_app.config.get('ORIGINALITY_PLAGIARISM_THRESHOLD', 0.70)
        if not (0.0 < threshold <= 1.0):
            raise ValueError()
    except ValueError:
        return error_response('score_threshold debe ser un numero entre 0.0 y 1.0.', 'Parametro invalido', 400)

    file_size = get_file_size(file)
    file_path, _ = save_upload(file)
    ext = get_file_extension(file.filename)
    user_id = get_jwt_identity()

    record = call_fn('fn_create_thesis_check', (
        file.filename, file_path, ext, file_size, user_id, threshold
    ), fetch_one=True)

    _run_check_async(current_app._get_current_object(), record['id'])

    return success_response(
        data={'check': format_thesis_check(record)},
        message='Verificacion iniciada. Procesando...',
        status_code=201
    )


def _run_check_async(app, check_id):
    def process():
        with app.app_context():
            from app.rag.originality import run_originality_check
            try:
                run_originality_check(check_id, app)
            except Exception as e:
                print(f'[Originality error] {check_id}: {e}')

    thread = threading.Thread(target=process)
    thread.daemon = True
    thread.start()


@originality_bp.route('/', methods=['GET'])
@role_required('admin')
def list_checks():
    page, per_page = get_pagination_params()
    status = request.args.get('status', '')

    rows = call_fn('fn_list_thesis_checks', ('', status, page, per_page), fetch_all=True)
    total = rows[0]['total_count'] if rows else 0
    items = [format_thesis_check(r) for r in rows]

    return paginated_response(items, total, page, per_page, 'Verificaciones obtenidas exitosamente.')


@originality_bp.route('/<check_id>', methods=['GET'])
@role_required('admin')
def get_check(check_id):
    record = call_fn('fn_get_thesis_check', (check_id,), fetch_one=True)
    if not record:
        return error_response('Verificacion no encontrada.', 'No encontrada', 404)
    return success_response(data={'check': format_thesis_check(record)})


@originality_bp.route('/<check_id>', methods=['DELETE'])
@role_required('admin')
def delete_check(check_id):
    result = call_fn('fn_delete_thesis_check', (check_id,), fetch_one=True)
    if not result or not result['fn_delete_thesis_check']:
        return error_response('Verificacion no encontrada.', 'No encontrada', 404)
    delete_file(result['fn_delete_thesis_check'])
    return success_response(message='Verificacion eliminada exitosamente.')
