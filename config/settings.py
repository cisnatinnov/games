"""
Secure configuration management for the Flask application.
Handles secrets, API keys, and security settings with proper defaults and validation.
"""
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration with secure defaults."""
    
    # Security Settings
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    JWT_SECRET = os.getenv('JWT_SECRET') or secrets.token_hex(32)
    
    # Warn if using generated secrets in production
    if not os.getenv('SECRET_KEY'):
        import warnings
        warnings.warn("SECRET_KEY not set in environment. Using auto-generated key. NOT suitable for production!")
    
    if not os.getenv('JWT_SECRET'):
        import warnings
        warnings.warn("JWT_SECRET not set in environment. Using auto-generated key. NOT suitable for production!")
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    
    # API Settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    API_BASE_URL = "https://api.alquran.cloud/v1"
    
    # Flask Settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    THREADED = True
    
    # Session Settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        errors = []
        
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is not set")
        
        return errors
    
    @staticmethod
    def create_upload_folder():
        """Ensure upload folder exists."""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        return Config.UPLOAD_FOLDER
