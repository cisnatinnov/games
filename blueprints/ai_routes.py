"""
AI and Media routes blueprint for chat, image generation, classification, and file uploads.
Includes secure file handling and proper validation.
"""
import os
import mimetypes
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from middleware.security import rate_limit, validate_json_required, sanitize_filename

ai_bp = Blueprint('ai', __name__, url_prefix='/')

# Import AI functions
from chat import chat, generate_image, classify_image

# Allowed MIME types for additional security
ALLOWED_MIME_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'image/gif': 'gif',
    'image/webp': 'webp'
}

def allowed_file_extension(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def validate_mime_type(filepath):
    """Validate file MIME type by reading magic bytes."""
    try:
        mime_type, _ = mimetypes.guess_type(filepath)
        return mime_type in ALLOWED_MIME_TYPES
    except Exception:
        return False

@ai_bp.route('/chat', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=60, window_seconds=3600)
def chat_op():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or empty text parameter'}), 400
    
    # Limit input length
    if len(text) > 5000:
        return jsonify({'status': 400, 'message': 'Text too long (max 5000 characters)'}), 400
    
    resp = chat(text)
    return jsonify({"reply": resp})

@ai_bp.route('/image', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=20, window_seconds=3600)
def image_route():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or empty text parameter'}), 400
    
    # Limit prompt length
    if len(text) > 1000:
        return jsonify({'status': 400, 'message': 'Prompt too long (max 1000 characters)'}), 400
    
    resp = generate_image(text)
    return jsonify({"image": resp})

@ai_bp.route('/classify_image', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=3600)
def classify_image_op():
    """Handle image classification with file upload and secure handling."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file_extension(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    prompt = request.form.get('prompt', "Describe this image in detail.")
    
    # Limit prompt length
    if len(prompt) > 1000:
        return jsonify({"error": "Prompt too long (max 1000 characters)"}), 400

    try:
        # Sanitize filename to prevent path traversal
        original_filename = file.filename or "uploaded_file"
        safe_filename = sanitize_filename(original_filename)
        
        if not safe_filename:
            return jsonify({"error": "Invalid filename"}), 400
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
        
        # Save file securely
        file.save(filepath)
        
        # Validate MIME type after saving
        if not validate_mime_type(filepath):
            os.remove(filepath)
            return jsonify({"error": "Invalid file content type"}), 400

        description = classify_image(prompt, filepath)

        # Clean up uploaded file immediately after processing
        try:
            os.remove(filepath)
        except OSError:
            pass

        return jsonify({
            "description": description,
            # Don't expose the file URL - security improvement
            "processed": True
        })
    except Exception as e:
        # Ensure cleanup on error
        try:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
        except OSError:
            pass
        return jsonify({"error": f"File processing failed: {str(e)}"}), 500

@ai_bp.route('/uploads/<path:filename>')
@rate_limit(max_requests=100, window_seconds=3600)
def uploaded_file(filename):
    """
    Serve uploaded files with security restrictions.
    Only serves files that exist and have valid extensions.
    """
    # Prevent path traversal attacks
    safe_filename = os.path.basename(filename)
    if safe_filename != filename:
        return jsonify({"error": "Invalid filename"}), 400
    
    if not allowed_file_extension(safe_filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    # Verify file exists and is within upload folder
    filepath = os.path.join(upload_folder, safe_filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    # Additional check to ensure file is within upload folder
    real_path = os.path.realpath(filepath)
    real_upload = os.path.realpath(upload_folder)
    if not real_path.startswith(real_upload):
        return jsonify({"error": "Access denied"}), 403
    
    return send_from_directory(upload_folder, safe_filename)
