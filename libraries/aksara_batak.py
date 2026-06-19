"""Placeholder mapping for Aksara Batak (identity mapping)."""
MAPPING = {ch: ch for ch in list('abcdefghijklmnopqrstuvwxyz ')}

def latin_to_aksara(text: str) -> str:
    return ''.join(MAPPING.get(ch, ch) for ch in text.lower())
