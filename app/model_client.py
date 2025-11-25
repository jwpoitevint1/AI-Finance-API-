import os
from app.governance import log_event

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "mock")
PROJECT_ID = os.getenv("PROJECT_ID", "")
LOCATION = os.getenv("LOCATION", "")
MODEL = os.getenv("MODEL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

FALLBACK_RESPONSE = os.getenv(
    "FALLBACK_RESPONSE",
    "This query couldn't be processed safely. Please rephrase or consult a verified source."
)

def call_model(prompt_text: str, role: str) -> str:
    try:
        if MODEL_PROVIDER == "gemini":
            import vertexai
            from vertexai.generative_models import GenerativeModel
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            model = GenerativeModel(MODEL)
            response = model.generate_content(prompt_text)
            return getattr(response, "text", FALLBACK_RESPONSE)

        elif MODEL_PROVIDER == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": role, "content": prompt_text}]
            )
            return response.choices[0].message.content

        elif MODEL_PROVIDER == "anthropic":
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=MODEL,
                max_tokens=700,
                messages=[{"role": role, "content": prompt_text}]
            )
            return response.content[0].text

        else:
            return f"[MOCK RESPONSE] role={role}, prompt={prompt_text[:50]}..."

    except Exception as e:
        log_event("fail_graceful_redirect", {"error": str(e), "prompt": prompt_text})
        return FALLBACK_RESPONSE
      
