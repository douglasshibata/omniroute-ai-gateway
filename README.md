# 🌐 OmniRoute AI Gateway

OmniRoute acts as a single, unified, OpenAI-compatible proxy interface that routes AI/LLM requests across multiple backend providers (OpenAI, Anthropic Claude, Google Gemini, DeepSeek, local Ollama instances) with dynamic model selection, automatic failover cascade, circuit-breaking resilience, and FinOps token telemetry.

Implemented directly following the architectural specifications in [`docs/blueprints/OMNIROUTE_INTEGRATION_BLUEPRINT.md`](../docs/blueprints/OMNIROUTE_INTEGRATION_BLUEPRINT.md).

---

## 🏛️ Architecture Overview

- **Standardized Ingress:** Exposes OpenAI v1 API endpoints (`/v1/chat/completions`, `/v1/models`, `/health`).
- **Dynamic Auto-Routing:** Translates `model: "auto"` into an intelligent multi-provider priority chain.
- **Circuit Breaker & Fallback:** Automatically switches to secondary/local providers upon consecutive provider errors.
- **FinOps Telemetry:** Returns token consumption and provider metadata in response headers (`x-omniroute-provider`, `x-omniroute-tokens-used`, `x-omniroute-model`).

---

## 🚀 Quickstart

```bash
# Run unit tests
PYTHONPATH=omniroute-ai-gateway pytest omniroute-ai-gateway/tests/

# Start server locally
cd omniroute-ai-gateway
uvicorn src.main:app --port 20128
```
