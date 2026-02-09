import os
import uuid
from flask import current_app


ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'xls', 'txt', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def save_upload(file):
    ext = get_file_extension(file.filename)
    unique_name = f"{uuid.uuid4()}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)
    return file_path, unique_name


def delete_file(file_path):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


def get_file_size(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size
