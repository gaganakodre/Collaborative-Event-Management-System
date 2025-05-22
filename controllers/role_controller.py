from functools import wraps
from flask_jwt_extended import get_jwt_identity
from utils.rds_helper import RDSHelper
from flask import jsonify

def role_required(allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            db = RDSHelper()
            result = db.execute_query("SELECT r.name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = %s", (user_id,))
            print(result)
            if not result or result[0]['name'] not in allowed_roles:
                return jsonify({"error": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
