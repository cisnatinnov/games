"""
API routes blueprint for NLP, Aksara, BMI, Morse code, and Quran API.
Includes proper input validation and security measures.
"""
from flask import Blueprint, request, jsonify
import requests
from middleware.security import rate_limit, validate_json_required, validate_positive_number

api_bp = Blueprint('api', __name__, url_prefix='/')

# Import library functions
from libraries.ner import analyze_text, analyze_summarize, text_generator, analyze_sentiment
from libraries.aksara_sunda import to_aksara_sunda
from libraries.aksara_jawa import to_aksara_jawa
from libraries.aksara_bali import to_aksara_bali
from libraries.securities import decode_morse, encode_morse

API_BASE_URL = "https://api.alquran.cloud/v1"

# Create a session for connection pooling (performance optimization)
api_session = requests.Session()
api_session.headers.update({'User-Agent': 'FlaskApp/1.0'})

@api_bp.route('/ner/tagging', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=100, window_seconds=3600)
def ner_tagging():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid text parameter'}), 400
    
    # Limit text length to prevent abuse
    if len(text) > 10000:
        return jsonify({'status': 400, 'message': 'Text too long (max 10000 characters)'}), 400
    
    resp = analyze_text(text)
    return jsonify(resp), resp.get('status', 200)

@api_bp.route('/ner/sentiment', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=100, window_seconds=3600)
def ner_sentiment():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid text parameter'}), 400
    
    if len(text) > 10000:
        return jsonify({'status': 400, 'message': 'Text too long (max 10000 characters)'}), 400
    
    resp = analyze_sentiment(text)
    return jsonify(resp), resp.get('status', 200)

@api_bp.route('/ner/summarize', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=50, window_seconds=3600)
def ner_summarize():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid text parameter'}), 400
    
    if len(text) > 50000:
        return jsonify({'status': 400, 'message': 'Text too long (max 50000 characters)'}), 400
    
    resp = analyze_summarize(text)
    return jsonify(resp), resp.get('status', 200)

@api_bp.route('/ner/generator', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=50, window_seconds=3600)
def ner_generator():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid text parameter'}), 400
    
    if len(text) > 5000:
        return jsonify({'status': 400, 'message': 'Text too long (max 5000 characters)'}), 400
    
    resp = text_generator(text)
    return jsonify(resp), resp.get('status', 200)

# ==================== Aksara Routes ====================

@api_bp.route('/aksara_sunda', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=200, window_seconds=3600)
def aksara_sunda_route():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid text parameter'}), 400
    
    if len(text) > 5000:
        return jsonify({'status': 400, 'message': 'Text too long (max 5000 characters)'}), 400
    
    resp = to_aksara_sunda(text)
    return jsonify(resp), resp.get('status', 200)

@api_bp.route('/aksara_jawa', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=200, window_seconds=3600)
def aksara_jawa_route():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid text parameter'}), 400
    
    if len(text) > 5000:
        return jsonify({'status': 400, 'message': 'Text too long (max 5000 characters)'}), 400
    
    resp = to_aksara_jawa(text)
    return jsonify(resp), resp.get('status', 200)

@api_bp.route('/aksara_bali', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=200, window_seconds=3600)
def aksara_bali_route():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid text parameter'}), 400
    
    if len(text) > 5000:
        return jsonify({'status': 400, 'message': 'Text too long (max 5000 characters)'}), 400
    
    resp = to_aksara_bali(text)
    return jsonify(resp), resp.get('status', 200)

# ==================== BMI Calculator ====================

@api_bp.route('/bmi', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=300, window_seconds=3600)
def bmi():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    weight = data.get('weight')
    height_cm = data.get('height')
    
    # Validate weight
    if weight is None:
        return jsonify({'status': 400, 'message': 'Missing weight parameter'}), 400
    
    weight_val, error = validate_positive_number(weight, 'weight')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    
    # Validate height
    if height_cm is None:
        return jsonify({'status': 400, 'message': 'Missing height parameter'}), 400
    
    height_val, error = validate_positive_number(height_cm, 'height')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    
    # Convert height from cm to meters
    height_m = height_val / 100
    
    # Calculate BMI
    try:
        bmi_value = weight_val / (height_m * height_m)
        bmi_rounded = round(bmi_value, 2)
    except ZeroDivisionError:
        return jsonify({'status': 400, 'message': 'Invalid height value'}), 400
    
    # Determine category
    if bmi_rounded <= 16:
        result = "You are very underweight"
    elif bmi_rounded <= 18.5:
        result = "You are underweight"
    elif bmi_rounded <= 25:
        result = "Congrats! You are Healthy"
    elif bmi_rounded <= 30:
        result = "You are overweight"
    else:
        result = "You are very overweight"
    
    return jsonify({
        'status': 200,
        'message': '',
        'data': {
            'bmi': bmi_rounded,
            'result': result
        }
    }), 200

# ==================== Morse Code ====================

@api_bp.route('/decode_morse', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=500, window_seconds=3600)
def decode_morse_op():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    morse = data.get('morse', '')
    if not morse or not isinstance(morse, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid morse parameter'}), 400
    
    # Limit morse code length
    if len(morse) > 5000:
        return jsonify({'status': 400, 'message': 'Morse code too long (max 5000 characters)'}), 400
    
    resp = decode_morse(morse)
    return jsonify({'status': 200, 'result': resp}), 200

@api_bp.route('/encode_morse', methods=['POST'])
@validate_json_required
@rate_limit(max_requests=500, window_seconds=3600)
def encode_morse_op():
    data = request.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'status': 400, 'message': 'Missing or invalid text parameter'}), 400
    
    if len(text) > 5000:
        return jsonify({'status': 400, 'message': 'Text too long (max 5000 characters)'}), 400
    
    resp = encode_morse(text)
    return jsonify({'status': 200, 'result': resp}), 200

# ==================== Quran API ====================

@api_bp.route('/api/surahs', methods=['GET'])
@rate_limit(max_requests=200, window_seconds=3600)
def get_surahs():
    """Fetches and returns a list of all surahs from the API."""
    try:
        response = api_session.get(f"{API_BASE_URL}/surah", timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.Timeout:
        return jsonify({'status': 504, 'message': 'API request timed out'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 502, 'message': f'External API error: {str(e)}'}), 502

@api_bp.route('/api/surah/<int:surah_number>', methods=['GET'])
@rate_limit(max_requests=200, window_seconds=3600)
def get_surah_details(surah_number):
    """Fetches and returns the details of a specific surah."""
    # Validate surah number (1-114)
    if surah_number < 1 or surah_number > 114:
        return jsonify({'status': 400, 'message': 'Invalid surah number (must be 1-114)'}), 400
    
    try:
        response = api_session.get(f"{API_BASE_URL}/surah/{surah_number}", timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.Timeout:
        return jsonify({'status': 504, 'message': 'API request timed out'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 502, 'message': f'External API error: {str(e)}'}), 502
