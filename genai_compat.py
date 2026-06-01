"""Compatibility wrapper that normalizes `google.genai` and `google.generativeai`.

Provides a minimal API surface used by this project:
- `configure(api_key=...)`
- `GenerativeModel` class with `generate_content()` method

The wrapper will prefer `google.genai` if available and fall back to
`google.generativeai`. It adapts differences where possible and falls
back to conservative behavior when an adapter path is not available.
"""
import os
import logging
from types import SimpleNamespace

# Provider selection: 'auto' (default) will prefer google.genai -> google.generativeai
# You may set GENAI_PROVIDER to 'openai' or 'mock' to force an alternative provider.
_provider = os.getenv('GENAI_PROVIDER', 'auto').lower()

_sdk = None
_sdk_name = None

# Track credential source for diagnostics: 'passed', 'env:OPENAI_API_KEY',
# 'env:GOOGLE_API_KEY', or None
_credential_source = None

if _provider in ('auto', 'genai'):
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
elif _provider == 'openai':
    try:
        import openai as _sdk
        _sdk_name = 'openai'
    except Exception:
        _sdk = None
        _sdk_name = None
elif _provider in ('mock', 'local_mock'):
    # no SDK required for mock
    _sdk = None
    _sdk_name = 'mock'
else:
    # unknown provider -> fall back to auto detection
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


def _init_provider(provider_hint=None):
    """Initialize _sdk and _sdk_name based on provider hint."""
    global _sdk, _sdk_name, _provider, _credential_source
    if provider_hint:
        _provider = provider_hint.lower()
    else:
        _provider = os.getenv('GENAI_PROVIDER', 'auto').lower()

    _sdk = None
    _sdk_name = None

    if _provider in ('auto', 'genai'):
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
    elif _provider == 'openai':
        try:
            import openai as _sdk
            _sdk_name = 'openai'
        except Exception:
            _sdk = None
            _sdk_name = None
    elif _provider in ('mock', 'local_mock'):
        _sdk = None
        _sdk_name = 'mock'
    else:
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


# Initialize provider at module import
_init_provider(_provider)

# Minimal startup detection logging
_logger = logging.getLogger(__name__)
# initial credential detection from environment
try:
    if _sdk_name == 'openai' and os.getenv('OPENAI_API_KEY'):
        _credential_source = 'env:OPENAI_API_KEY'
    elif _sdk_name in ('genai', 'generativeai') and os.getenv('GOOGLE_API_KEY'):
        _credential_source = 'env:GOOGLE_API_KEY'
    else:
        # if provider not detected yet, still record env keys if present
        if os.getenv('OPENAI_API_KEY'):
            _credential_source = 'env:OPENAI_API_KEY'
        elif os.getenv('GOOGLE_API_KEY'):
            _credential_source = 'env:GOOGLE_API_KEY'
except Exception:
    _credential_source = None

_logger.info('genai_compat startup provider=%s provider_hint=%s cred_source=%s', _sdk_name, _provider, _credential_source)


def configure(**kwargs):
    """Try to configure underlying SDK; if not available, set env var."""
    global _credential_source
    api_key = kwargs.get('api_key') or kwargs.get('apiKey') or kwargs.get('key')

    # If using OpenAI provider try to set its api key
    if _sdk_name == 'openai':
        # Prefer assigning into the openai module if possible, but many
        # client versions do not expose a writable `api_key` attribute.
        # Use setattr guarded by try/except and always set the environment
        # variable as a reliable fallback.
        if api_key:
            try:
                setattr(_sdk, 'api_key', api_key)
            except Exception:
                pass
            os.environ.setdefault('OPENAI_API_KEY', api_key)
            _credential_source = 'passed'
            return

        # If no explicit key passed, try the environment variable and
        # propagate it into the SDK when possible.
        if _sdk is not None:
            try:
                env_key = os.getenv('OPENAI_API_KEY')
                if env_key:
                    try:
                        setattr(_sdk, 'api_key', env_key)
                        _credential_source = 'env:OPENAI_API_KEY'
                    except Exception:
                        pass
            except Exception:
                pass
        return

    # If using mock or no SDK, just set env var for google key if present
    if _sdk is None:
        if api_key:
            os.environ.setdefault('GOOGLE_API_KEY', api_key)
            _credential_source = 'passed'
        return

    # If we have a detected SDK (google.genai / google.generativeai), try
    # calling its configure method with any provided api_key or the
    # GOOGLE_API_KEY environment variable.
    cfg = getattr(_sdk, 'configure', None)
    if callable(cfg):
        try:
            # prefer explicit api_key passed to configure()
            if api_key:
                _credential_source = 'passed'
                return cfg(api_key=api_key)
            # otherwise try env var
            gk = os.getenv('GOOGLE_API_KEY')
            if gk:
                try:
                    _credential_source = 'env:GOOGLE_API_KEY'
                    return cfg(api_key=gk)
                except Exception:
                    pass
        except Exception:
            pass

    # fallback: set environment variable if google api_key provided
    if api_key:
        os.environ.setdefault('GOOGLE_API_KEY', api_key)


def set_provider(provider, api_key=None):
    """Switch provider at runtime and (optionally) set API key.

    This updates module-level provider detection and attempts to
    configure the newly selected SDK.
    """
    global _provider, _credential_source
    _init_provider(provider)
    # ensure exported module-like object reflects updated internals
    try:
        _module._sdk = _sdk
        _module._sdk_name = _sdk_name
    except Exception:
        pass
    _provider = provider
    if api_key:
        configure(api_key=api_key)
    else:
        # attempt to configure from environment
        configure()
    _logger.info('Provider switched to %s (credential=%s)', _sdk_name, _credential_source)
    return _sdk_name


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
        # If user explicitly selected mock provider, don't try to bind SDK
        if _sdk_name == 'mock' or _provider in ('mock', 'local_mock'):
            # mock requires no underlying instance
            return

        # If OpenAI was selected use a small adapter
        if _sdk_name == 'openai' and _sdk is not None:
            # no wrapped instance, we'll call OpenAI directly in generate_content
            return

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
            # If mock provider requested, return a simple echo-like response
            if _sdk_name == 'mock' or _provider in ('mock', 'local_mock'):
                # Build a prompt string from args/kwargs
                try:
                    if args:
                        prompt = args[0]
                    else:
                        prompt = kwargs.get('prompt') or kwargs.get('text') or ''
                    # for lists join first element
                    if isinstance(prompt, (list, tuple)) and prompt:
                        prompt = prompt[0]
                    preview = (str(prompt)[:200] + '...') if isinstance(prompt, str) and len(str(prompt)) > 200 else str(prompt)
                except Exception:
                    preview = ''
                return SimpleNamespace(text=f"[MOCK RESPONSE] model={self._model_name} prompt={preview}")
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

        # If OpenAI SDK is available, adapt to it
        if _sdk_name == 'openai' and _sdk is not None:
            # Simple ChatCompletion-like call
            try:
                # Build prompt
                prompt = None
                if args:
                    prompt = args[0]
                else:
                    prompt = kwargs.get('prompt') or kwargs.get('text') or ''

                # If a list, assume first element is the main prompt
                if isinstance(prompt, (list, tuple)) and prompt:
                    prompt = prompt[0]

                # Build messages for chat API
                messages = []
                # If a system_instruction was provided in kwargs use it
                system = self._kwargs.get('system_instruction') or self._kwargs.get('system')
                if system:
                    messages.append({'role': 'system', 'content': system})
                messages.append({'role': 'user', 'content': str(prompt)})

                # Prefer ChatCompletion if present
                # Support new OpenAI client: `openai.OpenAI()`
                # Use safe attribute access to avoid triggering modules that
                # raise on attribute access (e.g. OpenAI shim that errors on
                # deprecated attributes like `ChatCompletion`). Prefer
                # checking the module dict first so we don't invoke
                # `__getattr__` implementations.
                def _safe_get_attr(mod, name):
                    d = getattr(mod, '__dict__', None)
                    if isinstance(d, dict) and name in d:
                        return d.get(name)
                    try:
                        return getattr(mod, name)
                    except Exception:
                        return None

                OpenAI = _safe_get_attr(_sdk, 'OpenAI')
                if OpenAI is not None:
                    try:
                        client = OpenAI()
                        # new client: client.chat.completions.create(...)
                        resp = client.chat.completions.create(model=self._model_name, messages=messages)
                        try:
                            text = resp.choices[0].message.content
                        except Exception:
                            text = getattr(resp, 'text', None) or getattr(resp, 'output', None) or str(resp)
                        return SimpleNamespace(text=text, raw=resp)
                    except Exception:
                        # fall through to other adapters
                        pass

                ChatCompletion = _safe_get_attr(_sdk, 'ChatCompletion')
                if ChatCompletion is not None:
                    try:
                        resp = ChatCompletion.create(model=self._model_name, messages=messages)
                        # Extract text from common locations
                        try:
                            text = resp.choices[0].message.content
                        except Exception:
                            text = getattr(resp, 'text', None) or getattr(resp, 'output', None) or str(resp)
                        return SimpleNamespace(text=text, raw=resp)
                    except Exception:
                        # If the underlying package raises an informative
                        # migration error when accessing deprecated attrs,
                        # fall through to next adapter instead of returning
                        # the raw error message.
                        pass

                # Fallback to completion.create
                Completion = _safe_get_attr(_sdk, 'Completion')
                if Completion is not None:
                    try:
                        resp = Completion.create(model=self._model_name, prompt=str(prompt), max_tokens=512)
                        try:
                            text = resp.choices[0].text
                        except Exception:
                            text = getattr(resp, 'text', None) or str(resp)
                        return SimpleNamespace(text=text, raw=resp)
                    except Exception:
                        pass
            except Exception as e:
                # Return informative error text rather than raising
                return SimpleNamespace(text=f'OpenAI adapter error: {str(e)}')

        # As a last resort return a graceful fallback response instead of
        # raising. Some installations may include the package but not expose
        # a compatible generation API; returning a small message keeps the
        # calling code (and UI) functional while providing actionable info.
        return SimpleNamespace(
            text=(
                'genai SDK present but no compatible generation API found. '
                'This installation of the SDK does not expose a supported '
                'generation entrypoint. Update to a supported package '
                "(google.genai) or check SDK version / environment settings."
            )
        )


# Expose a module-like object for easier replacement in imports
_module = SimpleNamespace()
_module.configure = configure
_module.GenerativeModel = GenerativeModel
_module._sdk = _sdk
_module._sdk_name = _sdk_name
_module.set_provider = set_provider
_module._credential_source = lambda: _credential_source

# Keep top-level name `genai` available if this file is imported directly
genai = _module

__all__ = ['genai', 'configure', 'GenerativeModel']
