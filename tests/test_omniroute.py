import pytest
from fastapi.testclient import TestClient
from src.main import app, router_engine
from src.router import MockProviderClient

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer omniroute-local-secret"}

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "providers" in data
    assert data["providers"]["openai"] is True

def test_models_unauthorized():
    res = client.get("/v1/models")
    assert res.status_code == 401

def test_models_authorized():
    res = client.get("/v1/models", headers=AUTH_HEADER)
    assert res.status_code == 200
    data = res.json()
    assert data["object"] == "list"
    models = [m["id"] for m in data["data"]]
    assert "auto" in models
    assert "gpt-4o" in models
    assert "claude-3-5-sonnet" in models

def test_chat_completion_auto():
    payload = {
        "model": "auto",
        "messages": [
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": "Explain microservices resiliency patterns."}
        ]
    }
    res = client.post("/v1/chat/completions", headers=AUTH_HEADER, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["object"] == "chat.completion"
    assert len(data["choices"]) > 0
    assert "Synthesized enterprise response" in data["choices"][0]["message"]["content"]
    assert res.headers["x-omniroute-provider"] == "openai"
    assert int(res.headers["x-omniroute-tokens-used"]) > 0

def test_chat_completion_failover():
    original_openai = router_engine.providers["openai"]
    router_engine.providers["openai"] = MockProviderClient("openai", fail=True)

    try:
        payload = {
            "model": "auto",
            "messages": [{"role": "user", "content": "Test failover routing"}]
        }
        res = client.post("/v1/chat/completions", headers=AUTH_HEADER, json=payload)
        assert res.status_code == 200
        assert res.headers["x-omniroute-provider"] == "anthropic"
        assert res.headers["x-omniroute-model"] == "claude-3-5-sonnet"
    finally:
        router_engine.providers["openai"] = original_openai

def test_circuit_breaker_tripping():
    failing_provider = MockProviderClient("test_failing", fail=True)
    assert failing_provider.is_healthy() is True

    for _ in range(3):
        try:
            failing_provider.generate([], "model")
        except RuntimeError:
            pass

    assert failing_provider.is_healthy() is False
