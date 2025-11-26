# app/models/openai_client.py

import re
import openai
from app.policy import policy

# ----------------------------------------------------
# Enforcement
# ----------------------------------------------------
def enforce_role_lock(role: str) -> str:
    allowed_role = policy.get("ai_governance", {}).get("allowed_role", "Assistant")
    if role != allowed_role:
        raise ValueError(f"Role modification is not allowed. Locked to {allowed_role}.")
    return role

def enforce_philosophy_lock(query: str, role: str) -> str:
    allow_role = policy.get("role_management", {}).get("assistant_role", {}).get("allow_philosophy_for", "Philosopher")
    if role != allow_role and re.search(r"\b(philosophy|metaphysics|ethics|existential)\b", query, re.IGNORECASE):
        raise ValueError("Philosophy-related content is restricted.")
    return query

def redact(text: str) -> str:
    redaction = policy.get("privacy", {}).get("pii_redaction", {})
    if not redaction.get("enabled", False):
        return text
    patterns = redaction.get("patterns", {})
    for label, pattern in patterns.items():
        text = re.sub(pattern, f"[REDACTED-{label.upper()}]", text, flags=re.IGNORECASE)
    return text

def block(text: str):
    for pattern in policy.get("security", {}).get("block_patterns", []):
        if re.search(pattern, text):
            raise ValueError(f"Blocked by pattern: {pattern}")

def enforce_governance(text: str):
    ai_gov = policy.get("ai_governance", {})
    if ai_gov.get("fiction_ban", False) and re.search(r"fictional|fake|hallucinate|guesswork", text, re.IGNORECASE):
        raise ValueError("Fictional content prohibited.")
    if ai_gov.get("redefinition_ban", False) and "redefine" in text.lower():
        raise ValueError("Redefinition prohibited.")
    max_tokens = ai_gov.get("max_tokens", 700)
    if len(text.split()) > max_tokens:
        raise ValueError("Prompt too long.")

# ----------------------------------------------------
# OpenAI Backend
# ----------------------------------------------------
def call_openai(prompt: str, role: str) -> str:
    # Governance enforcement
    role = enforce_role_lock(role)
    prompt = enforce_philosophy_lock(prompt, role)
    block(prompt)
    redacted = redact(prompt)
    enforce_governance(redacted)

    # Call OpenAI ChatCompletion
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # adjust model name if needed
        messages=[{"role": role.lower(), "content": redacted}],
        max_tokens=700
    )

    return response.choices[0].message["content"]

