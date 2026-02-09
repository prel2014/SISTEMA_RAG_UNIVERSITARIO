from flask import jsonify


def success_response(data=None, message='Operacion exitosa', status_code=200):
    response = {
        'success': True,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error_response(message='Ocurrio un error', error='Error', status_code=400):
    return jsonify({
        'success': False,
        'error': error,
        'message': message,
    }), status_code


def paginated_response(items, total, page, per_page, message='Datos obtenidos exitosamente'):
    return jsonify({
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
        }
    }), 200
