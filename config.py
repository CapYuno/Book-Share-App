"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bookshare.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SMTP Mail Configuration
    MAIL_SERVER = os.getenv('SMTP_HOST', 'localhost')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 1025))
    MAIL_USE_TLS = os.getenv('SMTP_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.getenv('SMTP_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('SMTP_USERNAME')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('SMTP_FROM', 'BookShare <noreply@bookshare.local>')
    
    # Reminder Settings
    REMINDER_BEFORE_DUE = int(os.getenv('REMINDER_BEFORE_DUE', 3))
    REMINDER_AFTER_DUE = int(os.getenv('REMINDER_AFTER_DUE', 3))
    
    # AI Recommendations
    RECOMMENDATIONS_TOP_K = int(os.getenv('RECOMMENDATIONS_TOP_K', 3))
    TF_IDF_MIN_DF = int(os.getenv('TF_IDF_MIN_DF', 2))
    TF_IDF_MAX_FEATURES = int(os.getenv('TF_IDF_MAX_FEATURES', 1000))
    TF_IDF_NGRAM_RANGE = tuple(map(int, os.getenv('TF_IDF_NGRAM_RANGE', '1,2').split(',')))
    RECOMMENDATION_CACHE_PATH = os.getenv('RECOMMENDATION_CACHE_PATH', 'tfidf_cache.pkl')
    
    # Performance
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 100))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
