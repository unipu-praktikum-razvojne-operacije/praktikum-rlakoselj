import pytest
import requests

import ollama_client


class FakeResponse:
    def __init__(self, data: dict, status_code: int = 200):
        self._data = data
        self.status_code = status_code
        self.text = str(data)

    def json(self) -> dict:
        return self._data


@pytest.fixture
def fake_request(monkeypatch):
    """Replaces requests.request and records every call it receives."""
    calls = []

    def install(response: FakeResponse | None = None, error: Exception | None = None):
        def fake(method, url, **kwargs):
            calls.append({"method": method, "url": url, **kwargs})
            if error:
                raise error
            return response

        monkeypatch.setattr(ollama_client.requests, "request", fake)
        return calls

    return install


def test_build_messages_puts_system_prompt_first():
    messages = ollama_client.build_messages("What is git?", system="Answer briefly.")

    assert messages == [
        {"role": "system", "content": "Answer briefly."},
        {"role": "user", "content": "What is git?"},
    ]





def test_list_models_returns_model_names(fake_request):
    response = FakeResponse({
        "models": [
            {"name": "llama3.2:1b"},
            {"name": "qwen2.5:0.5b"}
        ]
    })

    fake_request(response=response)

    models = ollama_client.list_models()

    assert models == ["llama3.2:1b", "qwen2.5:0.5b"]







def test_generate_sends_model_and_prompt_without_streaming(fake_request, monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    calls = fake_request(
        response=FakeResponse({"response": "Hello!"})
    )

    answer = ollama_client.generate("Say hello.")

    assert answer == "Hello!"
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["json"] == {
        "model": "test-model",
        "prompt": "Say hello.",
        "stream": False,
    }





def test_chat(fake_request):
    fake_request(response=FakeResponse({
        "message": {"content": "Hello!"}
    }))

    answer = ollama_client.chat([
        {"role": "user", "content": "Hi"}
    ])

    assert answer == "Hello!"




def test_generate_raises_ollama_error_when_server_is_down(fake_request):
    fake_request(error=requests.ConnectionError())

    with pytest.raises(ollama_client.OllamaError, match="not reachable"):
        ollama_client.generate("Hello")
