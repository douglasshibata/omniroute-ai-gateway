import uuid
import time
from fastapi import FastAPI, Depends, HTTPException, Security, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatChoiceMessage,
    UsageInfo,
    ModelListResponse,
    ModelItem,
)
from .config import config
from .router import OmniRouter

app = FastAPI(
    title="OmniRoute AI Gateway",
    description="Centralized OpenAI-compatible proxy interface with dynamic auto-routing, failover resilience, and FinOps token telemetry.",
    version="1.0.0"
)

security = HTTPBearer(auto_error=False)
router_engine = OmniRouter()

def verify_auth(credentials: HTTPAuthorizationCredentials = Security(security)):
    expected_key = config.api_key
    if not credentials or credentials.credentials != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing Bearer token")
    return credentials.credentials

@app.get("/health")
def health_check():
    providers_status = {name: p.is_healthy() for name, p in router_engine.providers.items()}
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "gateway": "omniroute",
        "providers": providers_status
    }

@app.get("/v1/models", response_model=ModelListResponse)
def list_models(auth: str = Depends(verify_auth)):
    models = router_engine.get_supported_models()
    return ModelListResponse(
        data=[ModelItem(id=m) for m in models]
    )

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(req: ChatCompletionRequest, response: Response, auth: str = Depends(verify_auth)):
    try:
        content, provider_name, resolved_model, p_tokens, c_tokens = router_engine.execute_completion(
            messages=req.messages,
            requested_model=req.model,
            temperature=req.temperature or 0.7
        )

        total_tokens = p_tokens + c_tokens

        response.headers["x-omniroute-provider"] = provider_name
        response.headers["x-omniroute-tokens-used"] = str(total_tokens)
        response.headers["x-omniroute-model"] = resolved_model

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
            model=resolved_model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatChoiceMessage(content=content)
                )
            ],
            usage=UsageInfo(
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                total_tokens=total_tokens
            )
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bad Gateway: {str(e)}")
