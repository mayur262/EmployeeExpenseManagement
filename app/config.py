import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')
    
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Santoshimata@208')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'expense_portal')

    USE_MYSQL = os.environ.get('USE_MYSQL', 'True').lower() == 'true'

    if USE_MYSQL:
        _encoded_password = quote_plus(os.environ.get('DB_PASSWORD', 'Santoshimata@208'))
        _db_user = os.environ.get('DB_USER', 'root')
        _db_host = os.environ.get('DB_HOST', 'localhost')
        _db_name = os.environ.get('DB_NAME', 'expense_portal')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_db_user}:{_encoded_password}@{_db_host}/{_db_name}"
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///expense_portal.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class TestingConfig(Config):
    TESTING = True
    USE_MYSQL = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
