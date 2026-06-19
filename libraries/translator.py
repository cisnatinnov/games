"""Translator utilities: connect Morse and aksara modules and provide a unified API.

This module provides simple wrappers around existing aksara modules and the
Morse utility. It also allows registering additional script mappings.
"""
from typing import Dict

from importlib import import_module

from . import morse

_MAPPINGS: Dict[str, Dict[str, str]] = {}


def _try_load_module(name: str):
    try:
        return import_module(f"libraries.aksara_{name}")
    except Exception:
        return None


def register_mapping(name: str, mapping: Dict[str, str]):
    """Register a character mapping for a named script.

    mapping should map latin characters (or strings) to target script strings.
    """
    _MAPPINGS[name.lower()] = mapping


def translate_to_script(script: str, text: str) -> str:
    """Translate `text` to `script` if mapping exists.

    Special-cases: 'morse' uses the morse utility.
    If a dedicated `libraries/aksara_{script}.py` module exists and exposes
    `latin_to_aksara` function or `MAPPING` dict, it will be used.
    Otherwise falls back to a best-effort character mapping or returns the
    original text.
    """
    key = script.lower()
    if key == 'morse':
        return morse.encode(text)

    # Check registered mappings
    if key in _MAPPINGS:
        mapping = _MAPPINGS[key]
        return ''.join(mapping.get(ch, ch) for ch in text)

    # Try to load a module libraries/aksara_{script}
    mod = _try_load_module(script)
    if mod:
        if hasattr(mod, 'latin_to_aksara'):
            try:
                return mod.latin_to_aksara(text)
            except Exception:
                pass
        if hasattr(mod, 'MAPPING'):
            mapping = getattr(mod, 'MAPPING')
            return ''.join(mapping.get(ch, ch) for ch in text)

    # Last-resort: return original text
    return text


def available_scripts():
    names = set(_MAPPINGS.keys()) | {"morse"}
    # scan common aksara modules
    for name in ('bali', 'jawa', 'sunda'):
        if _try_load_module(name):
            names.add(name)
    return sorted(names)
