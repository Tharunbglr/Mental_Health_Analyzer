import os
from typing import Optional, Dict, Any


def generate_ai_feedback(summary: Dict[str, Any]) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        # Lazy import to avoid hard dependency if not configured
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        system = (
            "You are a supportive, non-clinical assistant. Provide short, practical, and safe well-"
            "being suggestions. Avoid diagnostics or medical claims. Always encourage reaching out to"
            " trusted people or professionals when appropriate, and include a brief safety note if risk"
            " indicators appear. Keep it under 120 words."
        )
        user = (
            f"Name: {summary['name']} (age {summary['age']}). Mood: {summary['mood']}. "
            f"Sleep: {summary['sleep_hours']} hours. Stress: {summary['stress_level']}/5. "
            f"Notes: {summary['thoughts']!s}. Suggestions so far: {summary['suggestions']}"
        )

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
            max_tokens=220,
        )
        content = response.choices[0].message.content if response.choices else None
        return (content or "").strip() or None
    except Exception:
        return None


