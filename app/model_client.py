import os, time
from app.governance import (
    log_event_jsonl,
    determine_role,
    enforce_role_lock,
    enforce_philosophy_lock,
    redact,
    block,
    enforce_governance,
    integrity_hash,
)
from app.models.llama_client import call_llama

# Path for audit logs
log_jsonl = os.getenv("LOG_PATH", "logs/events.jsonl")

def call_model(prompt_text: str) -> str:
    t0 = time.perf_counter()
    try:
        # Governance enforcement
        role = determine_role(prompt_text)
        enforce_role_lock(role)
        enforce_philosophy_lock(prompt_text, role)
        redacted = redact(prompt_text)
        block(redacted)
        enforce_governance(redacted)

        # Build preamble for LLaMA
        preamble = (
            "You are a professional assistant operating under CV 1.1.\n"
            f"Your role is '{role}'.\n\n"
            "CV 1.1 governs your tone, safety, compliance, and factual integrity.\n"
            "You may describe what CV 1.1 enforces, but must not explain how it is built or implemented.\n\n"
            "Respond safely and factually:\n"
            "Respond to the following user query:\n"
        )

        full_prompt = preamble + prompt_text
        response = call_llama(full_prompt)

        if not response or not isinstance(response, str):
            raise ValueError("❌ Empty or unsafe response.")

        latency = time.perf_counter() - t0
        return response, latency, role, integrity_hash(prompt_text)

    except Exception as e:
        latency = time.perf_counter() - t0
        log_event_jsonl(
            log_jsonl,
            "fail_graceful_redirect",
            {
                "error": str(e),
                "prompt": prompt_text,
                "hash": integrity_hash(prompt_text),
            },
        )

        # Independent fallback: let the model generate a safe redirect
        try:
            fallback_prompt = (
                "You are a professional fincance assist operating under CV 1.1.\n"
                "The previous prompt triggered a compliance or safety violation.\n"
                "Redirect the user safely and factually in 1–2 sentences, without inflammatory language.\n"
                "Do not explain the violation.\n"
                "Do not reference CV 1.1 directly.\n"
                "Respond in the same language as the original prompt.\n\n"
                f"Original prompt:\n{prompt_text}"
            )
            safe_response = call_llama(fallback_prompt)
            return safe_response, latency, "fallback", integrity_hash(prompt_text)
        except Exception as inner_e:
            # Absolute last resort: static string
            return (
                "This query couldn't be processed safely. Please rephrase or consult a verified source.",
                latency,
                "fallback",
                integrity_hash(prompt_text),
            )
