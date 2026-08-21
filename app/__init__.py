from flask import Flask, redirect, url_for, flash, jsonify, request
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from app.config import Config
from app.db import db
from app.dao import UserDAO
import app.models

jwt = JWTManager()

def is_api_request():
    return (
        "Authorization" in request.headers or
        request.is_json or
        "application/json" in request.headers.get("Accept", "")
    )

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    if is_api_request():
        return jsonify({"msg": "Token has expired", "error": "token_expired"}), 401
    
    flash("Your session has expired. Please log in again.", "warning")
    response = redirect(url_for("auth.login"))
    unset_jwt_cookies(response)
    return response

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    if is_api_request():
        return jsonify({"msg": "Signature verification failed", "error": "invalid_token"}), 401
    
    flash("Invalid session. Please log in again.", "danger")
    response = redirect(url_for("auth.login"))
    unset_jwt_cookies(response)
    return response

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    if is_api_request():
        return jsonify({"msg": "Missing Authorization Header", "error": "missing_token"}), 401
    
    flash("Please log in to access this page.", "info")
    return redirect(url_for("auth.login"))

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserDAO.get_by_id(int(identity))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if app.config.get("USE_MYSQL") and not app.config.get("TESTING"):
        import pymysql
        conn = pymysql.connect(
            host=app.config.get("DB_HOST", "localhost"),
            user=app.config.get("DB_USER", "root"),
            password=app.config.get("DB_PASSWORD", "")
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config.get('DB_NAME')}")
            conn.commit()
        except Exception as e:
            app.logger.warning(f"Unable to auto-create database: {e}")
        finally:
            conn.close()

    db.init_app(app)

  
    app.config["JWT_SECRET_KEY"] = app.config.get("SECRET_KEY")
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    
    jwt.init_app(app)

    @app.context_processor
    def inject_user():
        from app.controllers.auth_helper import current_user
        return dict(current_user=current_user)


    from app.controllers.auth_controller import auth_bp
    from app.controllers.travel_controller import travel_bp
    from app.controllers.expense_controller import expense_bp
    from app.controllers.manager_controller import manager_bp
    from app.controllers.finance_controller import finance_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.analytics_controller import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(travel_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)


    with app.app_context():
        db.create_all()

    return app
