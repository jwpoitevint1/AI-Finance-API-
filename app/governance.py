# app/governance.py
import os, json, time, hmac, hashlib, logging, re, yaml, warnings
from typing import Dict, Any

warnings.filterwarnings("ignore", category=UserWarning)

# Files
LOG_FILE = os.getenv("LOG_FILE", "repls_audit.jsonl")
RESULT_FILE = os.getenv("RESULT_FILE", "repls_results.json")
SECRET_KEY = os.getenv("SECRET_KEY", "energy-session-key").encode()

# Logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(message)s")

def log_event(event_type: str, details: dict):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": event_type,
        "details": details
    }
    logging.info(json.dumps(entry))

# Load policy
def load_policy(path: str = "replspolicy.yaml") -> Dict[str, Any]:
    try:
        with open(os.path.abspath(path), "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        log_event("policy_load_error", {"error": str(e)})
        return {}

policy = load_policy()

# Enforcement
def enforce_role_lock(role: str) -> str:
    locked_role = policy.get("role_lock", {}).get("locked_role", "Assistant")
    allowed_roles = policy.get("role_lock", {}).get("allowed_roles", ["Assistant"])
    if role != locked_role and role not in allowed_roles:
        raise ValueError(f"Role modification is not allowed. Only: {', '.join(allowed_roles)}")
    return role

def enforce_philosophy_lock(query: str, role: str) -> str:
    allow_role = policy.get("philosophy_lock", {}).get("allow_philosophy_for", "Philosopher")
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

def integrity_hash(message: str) -> str:
    return hmac.new(SECRET_KEY, message.encode(), hashlib.sha256).hexdigest()

# Rate limiting (simple in-memory)
from collections import deque
from time import time as now

request_window = deque()
RATE_LIMIT = int(policy.get("security", {}).get("rate_limit_per_minute", 200))

def check_rate_limit() -> None:
    current = now()
    while request_window and current - request_window[0] > 60:
        request_window.popleft()
    if len(request_window) >= RATE_LIMIT:
        raise ValueError("Rate limit exceeded.")
    request_window.append(current)
