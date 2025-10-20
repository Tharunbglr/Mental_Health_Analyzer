from flask import Blueprint, render_template, request, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .ai import generate_ai_feedback


bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/test")
def test():
    return "App is working!"


@bp.post("/analyze")
def analyze():
    # Extract form values with simple validation
    name = (request.form.get("name") or "").strip()
    age_str = (request.form.get("age") or "").strip()
    mood = (request.form.get("mood") or "").strip().lower()
    sleep = (request.form.get("sleep") or "").strip()
    stress = (request.form.get("stress") or "").strip()
    thoughts = (request.form.get("thoughts") or "").strip()

    errors = {}
    if not name:
        errors["name"] = "Name is required."
    try:
        age = int(age_str)
        if age < 13 or age > 120:
            errors["age"] = "Enter a realistic age (13-120)."
    except ValueError:
        errors["age"] = "Age must be a number."

    valid_moods = {"very low", "low", "neutral", "good", "very good"}
    if mood not in valid_moods:
        errors["mood"] = "Select a mood option."

    try:
        sleep_hours = float(sleep)
        if sleep_hours < 0 or sleep_hours > 24:
            errors["sleep"] = "Enter hours between 0 and 24."
    except ValueError:
        errors["sleep"] = "Sleep must be a number."

    try:
        stress_level = int(stress)
        if stress_level < 1 or stress_level > 5:
            errors["stress"] = "Stress must be 1-5."
    except ValueError:
        errors["stress"] = "Stress must be a number."

    # Collect PHQ-9 and GAD-7 answers
    phq9 = []
    for i in range(1, 10):
        key = f"phq9_{i}"
        try:
            phq9.append(int(request.form.get(key, "")))
        except ValueError:
            errors[key] = "Required"

    gad7 = []
    for i in range(1, 8):
        key = f"gad7_{i}"
        try:
            gad7.append(int(request.form.get(key, "")))
        except ValueError:
            errors[key] = "Required"

    # Lifestyle
    try:
        exercise_days = int(request.form.get("exercise_days", ""))
    except ValueError:
        errors["exercise_days"] = "Required"
        exercise_days = 0
    try:
        caffeine_cups = int(request.form.get("caffeine_cups", ""))
    except ValueError:
        errors["caffeine_cups"] = "Required"
        caffeine_cups = 0
    try:
        screen_hours = float(request.form.get("screen_hours", ""))
    except ValueError:
        errors["screen_hours"] = "Required"
        screen_hours = 0.0
    try:
        support_level = int(request.form.get("support_level", ""))
        if support_level < 1 or support_level > 5:
            errors["support_level"] = "1-5"
    except ValueError:
        errors["support_level"] = "Required"
        support_level = 3

    if errors:
        return render_template(
            "index.html",
            errors=errors,
            form={
                "name": name,
                "age": age_str,
                "mood": mood,
                "sleep": sleep,
                "stress": stress,
                "thoughts": thoughts,
                **{f"phq9_{i}": request.form.get(f"phq9_{i}", "") for i in range(1, 10)},
                **{f"gad7_{i}": request.form.get(f"gad7_{i}", "") for i in range(1, 8)},
                "exercise_days": request.form.get("exercise_days", ""),
                "caffeine_cups": request.form.get("caffeine_cups", ""),
                "screen_hours": request.form.get("screen_hours", ""),
                "support_level": request.form.get("support_level", ""),
            },
        )

    # Simple rule-based analysis (safe, offline)
    suggestions = []
    risk_flag = False

    if mood in {"very low", "low"}:
        suggestions.append(
            "Your mood seems low. Consider small enjoyable activities and reaching out to someone you trust."
        )

    if sleep_hours < 6:
        suggestions.append(
            "You're sleeping less than recommended. Try a consistent bedtime and reduce screens before bed."
        )
    elif sleep_hours > 9:
        suggestions.append(
            "You're sleeping a lot. If this persists, consider discussing with a healthcare professional."
        )

    if stress_level >= 4:
        suggestions.append(
            "High stress reported. Try short breathing exercises, brief walks, or journaling."
        )

    if any(word in thoughts.lower() for word in ["hopeless", "harm", "suicide", "worthless"]):
        risk_flag = True
        suggestions.append(
            "If you feel unsafe or at risk of harming yourself, seek immediate help: local emergency services or a crisis hotline in your country."
        )

    if not suggestions:
        suggestions.append(
            "You're doing many things right. Keep monitoring your well-being and maintain supportive routines."
        )

    # Scoring helpers
    phq9_score = sum(phq9)
    if phq9_score <= 4:
        phq_level = "Minimal"
    elif phq9_score <= 9:
        phq_level = "Mild"
    elif phq9_score <= 14:
        phq_level = "Moderate"
    elif phq9_score <= 19:
        phq_level = "Moderately severe"
    else:
        phq_level = "Severe"

    gad7_score = sum(gad7)
    if gad7_score <= 4:
        gad_level = "Minimal"
    elif gad7_score <= 9:
        gad_level = "Mild"
    elif gad7_score <= 14:
        gad_level = "Moderate"
    else:
        gad_level = "Severe"

    # Lifestyle nudges
    if exercise_days < 2:
        suggestions.append("Consider adding 10–15 minute walks on 2+ days each week.")
    if caffeine_cups > 3:
        suggestions.append("High caffeine can impact anxiety and sleep; consider reducing gradually.")
    if screen_hours > 6:
        suggestions.append("Try short breaks and evening screen curfews to aid sleep and mood.")
    if support_level <= 2:
        suggestions.append("Think about one person you could check in with this week.")

    summary = {
        "name": name,
        "age": age,
        "mood": mood,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "thoughts": thoughts,
        "risk_flag": risk_flag,
        "suggestions": suggestions,
        "phq9_score": phq9_score,
        "phq9_level": phq_level,
        "gad7_score": gad7_score,
        "gad7_level": gad_level,
        "exercise_days": exercise_days,
        "caffeine_cups": caffeine_cups,
        "screen_hours": screen_hours,
        "support_level": support_level,
    }

    ai_feedback = None
    if request.form.get("use_ai") == "on":
        ai_feedback = generate_ai_feedback(summary)

    return render_template("result.html", summary=summary, ai_feedback=ai_feedback)


