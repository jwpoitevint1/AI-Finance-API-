from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.governance import block, redact, enforce_governance, enforce_role_lock, integrity_hash
from app.model_client import call_model

app = FastAPI(title="Finance AI Governance API")

class QueryRequest(BaseModel):
    prompt: str
    role: str = "Assistant"

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query")
def query(request: QueryRequest):
    try:
        role = enforce_role_lock(request.role)
        block(request.prompt)
        redacted = redact(request.prompt)
        enforce_governance(redacted)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response_text = call_model(redacted, role)

    return {
        "response": response_text,
        "redacted_prompt": redacted,
        "fallback": response_text.startswith("[MOCK RESPONSE]"),
        "hash": integrity_hash(response_text),
    }
