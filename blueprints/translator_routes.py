from flask import Blueprint, request, jsonify
import os

translator_bp = Blueprint('translator', __name__, url_prefix='/translator')


@translator_bp.route('/translate', methods=['POST'])
def translate_endpoint():
    data = request.get_json(force=True)
    target = data.get('target')
    text = data.get('text')
    if not target or not text:
        return jsonify({'status': 400, 'message': 'target and text required'}), 400

    # Lazy imports to avoid heavy dependencies at import time
    try:
        from games.libraries import translator
    except Exception:
        from libraries import translator

    model_path = os.path.join('models', 'translator.h5')
    toks_path = os.path.join('models', 'tokenizers.pkl')
    # If model exists, attempt model-based inference
    if os.path.exists(model_path) and os.path.exists(toks_path):
        try:
            try:
                from games.scripts.infer_translator import load_resources, greedy_decode
            except Exception:
                from scripts.infer_translator import load_resources, greedy_decode
            model, toks = load_resources(model_path, toks_path)
            out = greedy_decode(model, toks, text)
            return jsonify({'status': 200, 'target': target, 'input': text, 'output': out})
        except Exception:
            pass

    # Fallback to rule-based translator
    out = translator.translate_to_script(target, text)
    return jsonify({'status': 200, 'target': target, 'input': text, 'output': out})
