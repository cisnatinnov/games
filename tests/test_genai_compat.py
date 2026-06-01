import importlib
import os
import sys
import types
from types import SimpleNamespace


def test_mock_provider_response(tmp_path, monkeypatch):
    monkeypatch.setenv('GENAI_PROVIDER', 'mock')
    # ensure fresh import
    if 'genai_compat' in sys.modules:
        del sys.modules['genai_compat']
    import genai_compat
    importlib.reload(genai_compat)

    model = genai_compat.GenerativeModel('test-model')
    resp = model.generate_content('hello world')
    assert hasattr(resp, 'text')
    assert '[MOCK RESPONSE]' in resp.text
    assert 'test-model' in resp.text
    assert 'hello' in resp.text


def test_openai_adapter_with_fake_module(monkeypatch):
    # create a fake openai module with ChatCompletion
    fake_openai = types.SimpleNamespace()

    class FakeChatCompletion:
        @staticmethod
        def create(model, messages):
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='fake reply'))])

    fake_openai.ChatCompletion = FakeChatCompletion

    # inject into sys.modules
    sys.modules['openai'] = fake_openai

    monkeypatch.setenv('GENAI_PROVIDER', 'openai')
    monkeypatch.setenv('OPENAI_API_KEY', 'testkey')

    if 'genai_compat' in sys.modules:
        del sys.modules['genai_compat']
    import genai_compat
    importlib.reload(genai_compat)

    model = genai_compat.GenerativeModel('gpt-test')
    resp = model.generate_content('hi')
    assert hasattr(resp, 'text')
    assert resp.text == 'fake reply'
    # credential source should mention OPENAI
    assert genai_compat._credential_source and 'OPENAI' in genai_compat._credential_source