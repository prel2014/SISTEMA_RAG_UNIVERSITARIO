from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Solicitud invalida',
            'message': str(error.description) if hasattr(error, 'description') else 'Solicitud invalida'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'No autorizado',
            'message': 'Debe iniciar sesion para acceder a este recurso'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Acceso denegado',
            'message': 'No tiene permisos para acceder a este recurso'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'No encontrado',
            'message': 'El recurso solicitado no existe'
        }), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'success': False,
            'error': 'Archivo demasiado grande',
            'message': 'El archivo excede el tamano maximo permitido'
        }), 413

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 'Entidad no procesable',
            'message': str(error.description) if hasattr(error, 'description') else 'Datos invalidos'
        }), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ocurrio un error inesperado. Intente nuevamente.'
        }), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'success': False,
            'error': error.name,
            'message': error.description
        }), error.code
