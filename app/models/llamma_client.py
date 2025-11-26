# app/models/llama_client.py

import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
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
# LLaMA Backend
# ----------------------------------------------------
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"  # adjust to LLaMA 3 if desired
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

def call_llama(prompt: str, role: str) -> str:
    # Governance enforcement
    role = enforce_role_lock(role)
    prompt = enforce_philosophy_lock(prompt, role)
    block(prompt)
    redacted = redact(prompt)
    enforce_governance(redacted)

    # Generate response
    inputs = tokenizer(redacted, return_tensors="pt").to("cuda")
    outputs = model.generate(inputs["input_ids"], max_length=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
