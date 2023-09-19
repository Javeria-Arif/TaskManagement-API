from functools import wraps
from flask import jsonify, make_response, request
from helpers import decode_jwt
from models import User


def auth_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return make_response(jsonify({
                "error": "authentication token not found"
            }), 401)
        try:
            token = token.split("Bearer ")[1]
            data = decode_jwt(token)
            if data is None:
                raise Exception("invalid token")
            current_user = User.query.filter_by(id=data['user_id']).first()

            if current_user is None:
                raise Exception("invalid token")
        except Exception as e:
            print(e)
            return make_response(jsonify({
                "error": "invalid token"
            }), 401)
        return f(current_user, *args, **kwargs)
    return decorator
