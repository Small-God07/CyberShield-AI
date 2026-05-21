import os
from datetime import timedelta

class Config:
    """Configuration de base pour CyberShield-AI"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True') == 'True'
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Database SQL Server
    SQLSERVER_DRIVER = os.getenv('SQLSERVER_DRIVER', 'ODBC Driver 17 for SQL Server')
    SQLSERVER_SERVER = os.getenv('SQLSERVER_SERVER', 'localhost')
    SQLSERVER_DATABASE = os.getenv('SQLSERVER_DATABASE', 'CyberShield_AI')
    SQLSERVER_UID = os.getenv('SQLSERVER_UID', 'sa')
    SQLSERVER_PWD = os.getenv('SQLSERVER_PWD', '')
    
    # Connexion SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{SQLSERVER_UID}:{SQLSERVER_PWD}@"
        f"{SQLSERVER_SERVER}/{SQLSERVER_DATABASE}?"
        f"driver={SQLSERVER_DRIVER.replace(' ', '+')}"
    )
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # API
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200/hour"
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/cybershield.log'
    
    # Pagination
    ITEMS_PER_PAGE = 100

class DevelopmentConfig(Config):
    """Configuration pour développement"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cybershield_dev.db'

class ProductionConfig(Config):
    """Configuration pour production Windows Server"""
    DEBUG = False
    TESTING = False
    # En production, change ces variables d'environnement !
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("❌ SECRET_KEY environment variable must be set in production!")

class TestingConfig(Config):
    """Configuration pour tests"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Sélection de la config
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
