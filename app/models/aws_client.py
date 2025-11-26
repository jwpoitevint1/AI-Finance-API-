# app/models/aws_client.py

import re
import boto3
import os
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
# AWS Bedrock Backend
# ----------------------------------------------------
# Environment variables required:
#   AWS_REGION
#   AWS_ACCESS_KEY_ID
#   AWS_SECRET_ACCESS_KEY
#   BEDROCK_MODEL_ID (e.g., "anthropic.claude-v2", "cohere.command-r", "meta.llama2-13b-chat-v1")

def call_aws(prompt: str, role: str) -> str:
    # Governance enforcement
    role = enforce_role_lock(role)
    prompt = enforce_philosophy_lock(prompt, role)
    block(prompt)
    redacted = redact(prompt)
    enforce_governance(redacted)

    # Initialize Bedrock client
    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-v2")

    response = bedrock.invoke_model(
        modelId=model_id,
        body={
            "inputText": redacted,
            "parameters": {
                "maxTokens": 700,
                "temperature": 0.7
            }
        }
    )

    # Response parsing depends on the model provider
    output = response.get("body")
    if isinstance(output, dict) and "results" in output:
        return output["results"][0]["outputText"]
    return str(output)

