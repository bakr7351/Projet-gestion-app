import os
import logging
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def test_mysql_connection():
    """Test si MySQL est disponible"""
    db_type = os.environ.get("DB_TYPE", "sqlite")
    if db_type != "mysql":
        return False

    try:

        import pymysql
        mysql_host = os.environ.get("MYSQL_HOST", "localhost")
        mysql_port = int(os.environ.get("MYSQL_PORT", 3306))
        mysql_user = os.environ.get("MYSQL_USER", "absorption_user")
        mysql_password = os.environ.get("MYSQL_PASSWORD", "absorption_password")
        mysql_database = os.environ.get("MYSQL_DATABASE", "absorption_db")
        
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            connect_timeout=2,  # Timeout rapide
            charset='utf8mb4'
        )
        connection.close()
        return True
    except Exception as e:
        logging.getLogger(__name__).warning("MySQL connection test failed: %s", e)
        return False


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-me")

    # Database configuration avec fallback automatique
    DB_TYPE = os.environ.get("DB_TYPE", "sqlite")  # Par défaut SQLite
    
    # Configuration MySQL
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "absorption_user")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "absorption_password")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "absorption_db")
    
    # Configuration de l'URI avec fallback automatique
    if DB_TYPE == "mysql" and test_mysql_connection():
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
        )
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {'charset': 'utf8mb4'}
        }
        logging.getLogger(__name__).info("Configuration MySQL activée")

    else:
        # Fallback vers SQLite
        if DB_TYPE == "mysql":
            logging.getLogger(__name__).warning("MySQL non disponible, basculement vers SQLite")

        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            f"sqlite:///{os.path.join(os.path.dirname(BASE_DIR), 'database', 'absorption.db')}"
        )
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True
        }
        logging.getLogger(__name__).info("Configuration SQLite activée")

    
    # Autres configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail (SMTP)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@absorption.local")

    # Token expiry (seconds)
    EMAIL_TOKEN_EXPIRES = 86400   # 24h
    RESET_TOKEN_EXPIRES = 3600    # 1h

    # IP monitoring threshold
    SUSPICIOUS_IP_THRESHOLD = 3   # > 3 signups in 24h
