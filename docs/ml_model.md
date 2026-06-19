# Translator ML Model (Character-level seq2seq)

Summary
- Model type: character-level seq2seq (encoder LSTM + decoder LSTM) implemented with Keras/TensorFlow.
- Purpose: transliterate/translate Latin text into various Nusantara aksara (Jawa, Bali, Sunda, Minang, Malay, Batak, Bugis) or Morse.

Location
- Training script: `scripts/train_translator.py`
- Inference CLI: `scripts/infer_translator.py`
- Trained model saved to: `models/translator.h5`
- Tokenizers/state saved to: `models/tokenizers.pkl`
- Flask inference endpoint: `blueprints/translator_routes.py` (`/translator/translate`)
- Demo UI: `static/translate_demo.html`

Model details
- Input: Latin strings (character sequence). Encoder uses an Embedding + LSTM.
- Decoder: Embedding + LSTM with TimeDistributed Dense + softmax over output character vocabulary.
- Loss: sparse categorical crossentropy.
- Small, quick-to-train proof-of-concept. Parameters: embedding=64, latent=128 (see `train_translator.py`).

Dataset and training
- CSV format supported: two columns `latin` and `target` (header required). Pass via `--dataset path/to/file.csv`.
- Plain text files are supported: when `--dataset` points to a text file, the project will call the existing NER pipeline (`libraries/ner.analyze_text`) to extract candidate words/phrases to build Latin→target pairs automatically.
- If no dataset is supplied, `train_translator.py` falls back to a tiny built-in sample set.

How to train
1. Create and activate a venv; install requirements:
```bash
python -m pip install -r requirements.txt
```
2. Train a small model (example):
```bash
python -m games.scripts.train_translator --target jawa --epochs 10
```
3. Trained artifacts are written to `models/translator.h5` and `models/tokenizers.pkl`.

How to run inference
- CLI:
```bash
python -m games.scripts.infer_translator "salam"
```
- Flask API (if app running): POST JSON `{ "target": "jawa", "text": "salam" }` to `/translator/translate`.
- Demo UI: open `static/translate_demo.html` when the Flask app is running.

Notes and next steps
- Current `libraries/aksara_*` modules are placeholders (identity mapping) for some scripts (minang, malay, batak, bugis). Replace with real `MAPPING` dicts or `latin_to_aksara()` implementations and provide CSV datasets for better training.
- For production: save models in the native Keras format (`.keras`) or export for TFLite for edge/mobile.
- Consider switching to a Transformer-based model for better accuracy at scale or using subword tokenization if you need larger vocabularies.

Maintenance
- Keep `requirements.txt` updated for TF and NLP deps.
- Add CI task to run `python -m unittest` and optionally a smoke test that trains one epoch.

Contact
- File maintained by project scripts; see `scripts/train_translator.py` for implementation details.
