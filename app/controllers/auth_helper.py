from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_current_user as get_jwt_user
from werkzeug.local import LocalProxy

class AnonymousUser:
    id = None
    email = None
    role = None
    is_authenticated = False
    is_active = False
    is_anonymous = True

def _get_current_user():
    try:

        verify_jwt_in_request(optional=True)
        user = get_jwt_user()
        if user is not None:
            return user
    except Exception:
        pass
    return AnonymousUser()


current_user = LocalProxy(_get_current_user)

def login_required(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated_function
