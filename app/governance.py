import os
import json
import time
import hmac
import hashlib
import logging
import re
import yaml
import warnings
from typing import Dict, Any
from collections import deque
from time import time as now

warnings.filterwarnings("ignore", category=UserWarning)

# Files
LOG_FILE = os.getenv("LOG_FILE", "repls_audit.jsonl")
RESULT_FILE = os.getenv("RESULT_FILE", "repls_results.json")
SECRET_KEY = os.getenv("SECRET_KEY", "energy-session-key").encode()

# Logging -> writes JSON strings line-by-line to LOG_FILE via logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(message)s")

def log_event(event_type: str, details: dict):
    """Log event via Python logging (writes JSON to LOG_FILE)."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": event_type,
        "details": details
    }
    logging.info(json.dumps(entry))

def integrity_hash(message: str) -> str:
    """Compute HMAC-SHA256 integrity hash for a message."""
    return hmac.new(SECRET_KEY, message.encode(), hashlib.sha256).hexdigest()

def log_event_jsonl(event_type: str, details: dict, filepath: str = LOG_FILE):
    """Append event as a JSON line to the given file, with integrity hash and fail-safe fallback."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": event_type,
        "details": details,
        "integrity": integrity_hash(json.dumps(details))
    }
    try:
        with open(filepath, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        # fall back to standard logger so errors are never silent
        log_event("jsonl_write_error", {"error": str(e), "event_type": event_type})

# Load policy
def load_policy(path: str = "fintech-policy.yaml") -> Dict[str, Any]:
    try:
        with open(os.path.abspath(path), "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        log_event_jsonl("policy_load_error", {"error": str(e), "path": path})
        return {}

policy = load_policy()

# Role determination and enforcement
def determine_role(query: str, default_role: str = "Assistant") -> str:
    """
    Determine the role from policy, then enforce the lock.
    - If policy.ai_governance.allowed_role exists, use it; otherwise fallback to default_role.
    - Enforce role lock to prevent modification outside governance.
    """
    configured = policy.get("ai_governance", {}).get("allowed_role", default_role)
    role = configured
    try:
        enforced = enforce_role_lock(role)
        return enforced
    except Exception as e:
        log_event_jsonl("role_lock_violation", {"error": str(e), "requested_role": role})
        raise

# Enforcement
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

# Rate limiting (simple in-memory)
request_window = deque()
RATE_LIMIT = int(policy.get("security", {}).get("rate_limit_per_minute", 200))

def check_rate_limit() -> None:
    current = now()
    while request_window and current - request_window[0] > 60:
        request_window.popleft()
    if len(request_window) >= RATE_LIMIT:
        raise ValueError("Rate limit exceeded.")
    request_window.append(current)
