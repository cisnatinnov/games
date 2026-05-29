"""Compatibility wrapper that normalizes `google.genai` and `google.generativeai`.

Provides a minimal API surface used by this project:
- `configure(api_key=...)`
- `GenerativeModel` class with `generate_content()` method

The wrapper will prefer `google.genai` if available and fall back to
`google.generativeai`. It adapts differences where possible and falls
back to conservative behavior when an adapter path is not available.
"""
import os
from types import SimpleNamespace

_sdk = None
_sdk_name = None

try:
    import google.genai as _sdk
    _sdk_name = 'genai'
except Exception:
    try:
        import google.generativeai as _sdk
        _sdk_name = 'generativeai'
    except Exception:
        _sdk = None
        _sdk_name = None


def configure(**kwargs):
    """Try to configure underlying SDK; if not available, set env var."""
    if _sdk is None:
        return
    # best-effort: call configure if present
    cfg = getattr(_sdk, 'configure', None)
    if callable(cfg):
        try:
            return cfg(**kwargs)
        except Exception:
            pass
    # fallback: set environment variable if api_key provided
    api_key = kwargs.get('api_key') or kwargs.get('apiKey')
    if api_key:
        os.environ.setdefault('GOOGLE_API_KEY', api_key)


class GenerativeModel:
    """Adapter exposing a `generate_content` method similar to older SDKs.

    This will attempt to instantiate the SDK's native GenerativeModel
    implementation when available and delegate to it. Otherwise it will
    try commonly-named top-level generate functions.
    """

    def __init__(self, model_name, **kwargs):
        self._model_name = model_name
        self._kwargs = kwargs
        self._inst = None

        if _sdk is None:
            return

        # Try to use an existing GenerativeModel class from the SDK
        Under = getattr(_sdk, 'GenerativeModel', None)
        if Under:
            try:
                # try passing kwargs (some variants accept system_instruction)
                self._inst = Under(model_name, **kwargs)
            except TypeError:
                try:
                    # older signature may expect positional model name only
                    self._inst = Under(model_name)
                except Exception:
                    self._inst = None

    def generate_content(self, *args, **kwargs):
        """Delegate to the underlying instance or try top-level helpers.

        Returns whatever the SDK returns; callers should handle multiple
        response shapes (text, parts, file_data, etc.).
        """
        # If we have a wrapped instance delegate directly
        if self._inst is not None:
            return self._inst.generate_content(*args, **kwargs)

        if _sdk is None:
            raise RuntimeError('No genai SDK installed')

        # Try common top-level generator functions
        candidates = ['generate_content', 'generate', 'generate_text', 'text_generate']
        for name in candidates:
            fn = getattr(_sdk, name, None)
            if callable(fn):
                try:
                    # some functions expect model name first
                    try:
                        return fn(self._model_name, *args, **kwargs)
                    except TypeError:
                        return fn(*args, **kwargs)
                except Exception:
                    # try next candidate
                    pass

        # As a last resort raise informative error
        raise RuntimeError('genai SDK present but no compatible generation API found')


# Expose a module-like object for easier replacement in imports
_module = SimpleNamespace()
_module.configure = configure
_module.GenerativeModel = GenerativeModel
_module._sdk = _sdk
_module._sdk_name = _sdk_name

# Keep top-level name `genai` available if this file is imported directly
genai = _module

__all__ = ['genai', 'configure', 'GenerativeModel']
