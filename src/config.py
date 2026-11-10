import os
from typing import Dict, Any

class OmniRouteConfig:
    def __init__(self):
        self.port: int = int(os.getenv("PORT", "20128"))
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.api_key: str = os.getenv("OMNIROUTE_API_KEY", "omniroute-local-secret")
        self.default_model: str = os.getenv("OMNIROUTE_DEFAULT_MODEL", "auto")
        self.timeout_ms: int = int(os.getenv("OMNIROUTE_TIMEOUT_MS", "30000"))

        # Provider configurations
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

config = OmniRouteConfig()
