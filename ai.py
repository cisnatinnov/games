"""
Refactored Flask Application with Security Improvements

This is the main application entry point, refactored to use blueprints
for better organization and maintainability.

Security improvements:
- Removed dangerous eval() usage (scientific calculator)
- Secure file upload handling with MIME validation
- Strong JWT secret enforcement
- Rate limiting on all endpoints
- Input validation and sanitization
- Security headers
- Debug mode disabled by default
"""
import os
from flask import Flask, send_from_directory, jsonify
from config.settings import Config
from middleware.security import add_security_headers

# Import blueprints
from blueprints.math_routes import math_bp
from blueprints.api_routes import api_bp
from blueprints.ai_routes import ai_bp
from blueprints.games_routes import games_bp


def create_app(config_class=Config):
    """Application factory for creating Flask app instance."""
    
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Create upload folder
    config_class.create_upload_folder()
    
    # Validate configuration
    errors = config_class.validate()
    if errors:
        import warnings
        for error in errors:
            warnings.warn(f"Configuration warning: {error}")
    
    # Register blueprints
    app.register_blueprint(math_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(games_bp)
    
    # Add security headers to all responses
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)
    
    # Static routes
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'version': '2.0.0'})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'status': 404, 'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'status': 500, 'message': 'Internal server error'}), 500
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({'status': 429, 'message': 'Rate limit exceeded. Please try again later.'}), 429
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    # Production-ready configuration
    # Use environment variable to control debug mode
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    if debug_mode:
        import warnings
        warnings.warn("DEBUG MODE ENABLED - DO NOT USE IN PRODUCTION!")
    
    # Run with production settings
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=debug_mode,
        threaded=True
    )
