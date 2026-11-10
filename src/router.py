import os
import time
import uuid
from typing import List, Dict, Any, Tuple, Optional
from .models import ChatMessage

class ProviderClient:
    def __init__(self, name: str, is_available: bool = True):
        self.name = name
        self.is_available = is_available
        self.failure_count = 0
        self.circuit_open_until = 0.0

    def is_healthy(self) -> bool:
        if not self.is_available:
            return False
        if time.time() < self.circuit_open_until:
            return False
        return True

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= 3:
            self.circuit_open_until = time.time() + 30.0

    def record_success(self):
        self.failure_count = 0
        self.circuit_open_until = 0.0

    def generate(self, messages: List[ChatMessage], model: str, temperature: float = 0.7) -> Tuple[str, int, int]:
        raise NotImplementedError


class MockProviderClient(ProviderClient):
    def __init__(self, name: str, mock_response: Optional[str] = None, fail: bool = False):
        super().__init__(name, is_available=True)
        self.mock_response = mock_response
        self.fail = fail

    def generate(self, messages: List[ChatMessage], model: str, temperature: float = 0.7) -> Tuple[str, int, int]:
        if not self.is_healthy() or self.fail:
            self.record_failure()
            raise RuntimeError(f"Provider {self.name} is unavailable or failed.")

        user_content = " ".join([m.content for m in messages if m.role == "user"])
        prompt_tokens = max(10, len(user_content.split()) * 2)
        resp_text = self.mock_response or f"[{self.name}] Synthesized enterprise response for: {user_content}"
        completion_tokens = max(15, len(resp_text.split()) * 2)

        self.record_success()
        return resp_text, prompt_tokens, completion_tokens


class OmniRouter:
    def __init__(self):
        self.providers: Dict[str, ProviderClient] = {
            "openai": MockProviderClient("openai"),
            "anthropic": MockProviderClient("anthropic"),
            "gemini": MockProviderClient("gemini"),
            "deepseek": MockProviderClient("deepseek"),
            "ollama": MockProviderClient("ollama"),
        }

    def register_provider(self, name: str, provider: ProviderClient):
        self.providers[name] = provider

    def get_supported_models(self) -> List[str]:
        return [
            "auto",
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3-5-sonnet",
            "gemini-1.5-pro",
            "deepseek-chat",
            "llama3:8b",
            "qwen2.5:7b",
        ]

    def resolve_provider_chain(self, requested_model: str) -> List[Tuple[str, str]]:
        if requested_model == "auto":
            return [
                ("openai", "gpt-4o"),
                ("anthropic", "claude-3-5-sonnet"),
                ("gemini", "gemini-1.5-pro"),
                ("deepseek", "deepseek-chat"),
                ("ollama", "llama3:8b"),
            ]

        if "gpt" in requested_model:
            return [("openai", requested_model), ("deepseek", "deepseek-chat"), ("ollama", "llama3:8b")]
        elif "claude" in requested_model:
            return [("anthropic", requested_model), ("openai", "gpt-4o"), ("ollama", "llama3:8b")]
        elif "gemini" in requested_model:
            return [("gemini", requested_model), ("openai", "gpt-4o-mini"), ("ollama", "llama3:8b")]
        elif "deepseek" in requested_model:
            return [("deepseek", requested_model), ("openai", "gpt-4o-mini"), ("ollama", "llama3:8b")]
        elif "llama" in requested_model or "qwen" in requested_model or "ollama" in requested_model:
            return [("ollama", requested_model), ("deepseek", "deepseek-chat")]

        return [("openai", requested_model), ("ollama", "llama3:8b")]

    def execute_completion(self, messages: List[ChatMessage], requested_model: str, temperature: float = 0.7) -> Tuple[str, str, str, int, int]:
        cascade = self.resolve_provider_chain(requested_model)
        last_error = None

        for provider_name, model_name in cascade:
            provider = self.providers.get(provider_name)
            if not provider or not provider.is_healthy():
                continue

            try:
                response_text, p_tokens, c_tokens = provider.generate(messages, model_name, temperature)
                return response_text, provider_name, model_name, p_tokens, c_tokens
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All providers in fallback cascade failed. Last error: {last_error}")
