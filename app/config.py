import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')

    USE_MYSQL = os.getenv('USE_MYSQL', 'False').lower() == 'true'

    if USE_MYSQL:
        _encoded_password = quote_plus(DB_PASSWORD or '')
        _db_user = DB_USER or ''
        _db_host = DB_HOST or ''
        _db_name = DB_NAME or ''
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_db_user}:{_encoded_password}@{_db_host}/{_db_name}"
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///expense_portal.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class TestingConfig(Config):
    TESTING = True
    USE_MYSQL = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
