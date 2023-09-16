from functools import wraps
from os import environ
from flask import request, jsonify

def require_api_key(view_function=None, *, key=None, header_name='x-api-key'):
    api_key = key if key else environ.get('API_KEY')
    if not api_key:
        raise ValueError('API key is not set')
    if view_function is None:
        return lambda view_function: require_api_key(view_function, key=key, header_name=header_name)

    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get(header_name) == api_key:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"message": "Invalid API key"}), 403

    if not hasattr(decorated_function, '__apidoc__'):
        decorated_function.__apidoc__ = {}

    decorated_function.__apidoc__.setdefault('params', {})[header_name] = {
        'description': 'API key for authorization',
        'in': 'header',
        'type': 'string',
        'required': 'true'
    }

    return decorated_function