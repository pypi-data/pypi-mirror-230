import os
from interceptors import verify_admin_token, verify_user_token
from flask import request, abort, jsonify, make_response
from functools import wraps

USERNAME = os.environ['USERNAME_FLASK']


def require_user_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('x-api-key') and \
           verify_user_token(request.headers.get('x-api-key')):
            return view_function(*args, **kwargs)
        else:
            abort(make_response(jsonify({'error': {'statusCode': 401,
                                        'message': 'Invalid x-api-key'}}),
                                401))
    return decorated_function



def require_admin_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # print(f"Auth => {request.headers.get('Authorization', None)}")
        # print(f"Username => {USERNAME}")
        auth = request.headers.get('Authorization', None)
        if auth:
            if auth.startswith('Bearer'):
                split = auth.split("Bearer")
                access_token = split[1].strip()
                if verify_admin_token(access_token, USERNAME):
                    return view_function(*args, **kwargs)
                else:
                    abort(make_response(jsonify({'error': {'statusCode': 401,
                                                'message': 'Invalid token. Admins access only.'}}),
                                        401))
            else:
                abort(make_response(jsonify({'error': {'statusCode': 401,
                                            'message': 'Invalid token. The token should be Bearer.'}}),
                                    401))
        else:
            abort(make_response(jsonify({'error': {'statusCode': 401,
                                        'message': 'Please, provide a valid token.'}}),
                                401))
    return decorated_function
