from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.governance import block, redact, enforce_governance, enforce_role_lock, integrity_hash
from app.model_use import call_model  # Adjusted import

app = FastAPI(title="Finance Governance API")  # Removed 'AI' from title for neutrality

class QueryRequest(BaseModel):
    prompt: str
    role: str = "Assistant"

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query")
def query(request: QueryRequest):
    try:
        # Enforce role lock and governance checks before passing to model
        role = enforce_role_lock(request.role)
        block(request.prompt)
        redacted = redact(request.prompt)
        enforce_governance(redacted)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # call_model returns (response, latency, role, hash)
        response_text, latency, used_role, prompt_hash = call_model(redacted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")

    return {
        "response": response_text,
        "redacted_prompt": redacted,
        "fallback": used_role == "fallback",
        "latency": latency,
        "role": used_role,
        "hash": prompt_hash,
    }
