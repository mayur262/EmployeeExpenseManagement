from functools import wraps
from flask import render_template, abort
from app.controllers.auth_helper import current_user

def role_required(*roles):
    """
    Decorator to restrict view access to users with specified roles.
    Example: @role_required('Manager', 'Admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)  # Unauthorized
            if current_user.role not in roles:
                return render_template('unauthorized.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
