# app/model_client.py

import os
from app.governance import log_event
from app.models.openai_client import call_openai
from app.models.anthropic_client import call_anthropic
from app.models.vertex_client import call_vertex
from app.models.cohere_client import call_cohere
from app.models.azure_client import call_azure
from app.models.aws_client import call_aws
from app.models.llama_client import call_llama
from app.models.llama_cpp_client import call_llama_cpp

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "mock")

FALLBACK_RESPONSE = os.getenv(
    "FALLBACK_RESPONSE",
    "This query couldn't be processed safely. Please rephrase or consult a verified source."
)

def call_model(prompt_text: str, role: str) -> str:
    try:
        if MODEL_PROVIDER == "gemini":
            return call_vertex(prompt_text, role)
        elif MODEL_PROVIDER == "openai":
            return call_openai(prompt_text, role)
        elif MODEL_PROVIDER == "anthropic":
            return call_anthropic(prompt_text, role)
        elif MODEL_PROVIDER == "cohere":
            return call_cohere(prompt_text, role)
        elif MODEL_PROVIDER == "azure":
            return call_azure(prompt_text, role)
        elif MODEL_PROVIDER == "aws":
            return call_aws(prompt_text, role)
        elif MODEL_PROVIDER == "llama":
            return call_llama(prompt_text, role)
        elif MODEL_PROVIDER == "llama_cpp":
            return call_llama_cpp(prompt_text, role)
        else:
            return f"[MOCK RESPONSE] role={role}, prompt={prompt_text[:50]}..."
    except Exception as e:
        log_event("fail_graceful_redirect", {"error": str(e), "prompt": prompt_text})
        return FALLBACK_RESPONSE
