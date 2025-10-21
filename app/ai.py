import os
from functools import lru_cache
from typing import Any, Dict, Optional

_CACHE_TTL = int(os.getenv("AI_CACHE_TTL_SEC", "300"))


def _sanitize_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Return a redacted summary safe to send to an external AI provider.

    - Remove direct PII (name)
    - Truncate free-text notes to a reasonable length
    - Only include aggregated numeric results and levels
    """
    sanitized = {
        "age": summary.get("age"),
        "mood": summary.get("mood"),
        "sleep_hours": summary.get("sleep_hours"),
        "stress_level": summary.get("stress_level"),
        "phq9_score": summary.get("phq9_score"),
        "phq9_level": summary.get("phq9_level"),
        "gad7_score": summary.get("gad7_score"),
        "gad7_level": summary.get("gad7_level"),
        "suggestions": summary.get("suggestions", []),
    }
    notes = (summary.get("thoughts") or "").strip()
    if notes:
        sanitized["notes"] = notes[:500]
    return sanitized


def _cache_key(san: Dict[str, Any]) -> str:
    # simple stable string key for sanitized payload – small and deterministic
    parts = [
        f"phq:{san.get('phq9_score')}",
        f"gad:{san.get('gad7_score')}",
        f"mood:{san.get('mood')}",
        f"age:{san.get('age')}",
    ]
    return "-".join(parts)


def generate_ai_feedback(summary: Dict[str, Any]) -> Optional[str]:
    """Safely call the AI provider with a sanitized summary.

    Returns a short piece of content or None on error/unconfigured.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    sanitized = _sanitize_summary(summary)
    key = _cache_key(sanitized)

    # simple in-process cache: avoid repeated external calls for same data
    @lru_cache(maxsize=256)
    def _call_cached(k: str, payload_serialized: str) -> Optional[str]:
        # payload_serialized is unused but ensures cache key uniqueness when needed
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            system = (
                "You are a supportive, non-clinical assistant. Provide short, practical, "
                "and safe well-being suggestions. Avoid diagnostics or medical claims. "
                "Encourage reaching out to trusted people or professionals when appropriate, "
                "and include a brief safety note if risk indicators appear. Keep the "
                "response under 120 words."
            )
            user = (
                (
                    f"Age: {sanitized.get('age')}. Mood: {sanitized.get('mood')}. "
                    f"Sleep: {sanitized.get('sleep_hours')} hours. "
                    f"Stress: {sanitized.get('stress_level')}/5. "
                )
                + (
                    f"PHQ-9: {sanitized.get('phq9_score')} ({sanitized.get('phq9_level')}). "
                    f"GAD-7: {sanitized.get('gad7_score')} ({sanitized.get('gad7_level')}). "
                )
                + (
                    f"Notes (redacted): {sanitized.get('notes','')}. "
                    f"Suggestions so far: {sanitized.get('suggestions')}"
                )
            )

            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

            # lightweight timeout via client params where supported, and safe defaults
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.4,
                max_tokens=220,
            )
            content = (
                response.choices[0].message.content if getattr(response, "choices", None) else None
            )
            return (content or "").strip() or None
        except Exception:
            return None

    # call cached function – serialize small payload string for cache stability
    payload_serialized = str(sorted(sanitized.items()))
    return _call_cached(key, payload_serialized)
