import os

# ruff: noqa
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")


@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mental Health Analyzer</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #0f172a; color: #e5e7eb; }
            .card { background: #111827; padding: 30px; border-radius: 12px; margin: 20px 0; }
            h1 { color: #60a5fa; text-align: center; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #243046; border-radius: 8px; background: #0b1020; color: #e5e7eb; }
            button { background: #2563eb; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
            button:hover { background: #1d4ed8; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Mental Health Analyzer</h1>
            <p style="text-align: center; color: #93c5fd;">Personalized, informative suggestions — not medical advice</p>
            
            <form method="post" action="/analyze">
                <div class="form-group">
                    <label for="name">Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div class="form-group">
                    <label for="age">Age</label>
                    <input type="number" id="age" name="age" min="13" max="120" required>
                </div>
                
                <div class="form-group">
                    <label for="mood">Mood</label>
                    <select id="mood" name="mood" required>
                        <option value="">Select...</option>
                        <option value="very low">Very Low</option>
                        <option value="low">Low</option>
                        <option value="neutral">Neutral</option>
                        <option value="good">Good</option>
                        <option value="very good">Very Good</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="sleep">Sleep (hours last night)</label>
                    <input type="number" id="sleep" name="sleep" step="0.5" min="0" max="24" required>
                </div>
                
                <div class="form-group">
                    <label for="stress">Stress Level (1-5)</label>
                    <input type="number" id="stress" name="stress" min="1" max="5" required>
                </div>
                
                <div class="form-group">
                    <label for="thoughts">Notes (optional)</label>
                    <textarea id="thoughts" name="thoughts" rows="4" placeholder="Anything else on your mind?"></textarea>
                </div>
                
                <button type="submit">Analyze</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.route("/analyze", methods=["POST"])
def analyze():
    name = request.form.get("name", "")
    age = request.form.get("age", "")
    mood = request.form.get("mood", "")
    sleep = request.form.get("sleep", "")
    stress = request.form.get("stress", "")
    thoughts = request.form.get("thoughts", "")

    # Simple analysis
    suggestions = []
    if mood in ["very low", "low"]:
        suggestions.append(
            "Your mood seems low. Consider small enjoyable activities and reaching out to someone you trust."
        )

    if float(sleep) < 6:
        suggestions.append(
            "You're sleeping less than recommended. Try a consistent bedtime and reduce screens before bed."
        )

    if int(stress) >= 4:
        suggestions.append(
            "High stress reported. Try short breathing exercises, brief walks, or journaling."
        )

    if not suggestions:
        suggestions.append(
            "You're doing many things right. Keep monitoring your well-being and maintain supportive routines."
        )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Results - Mental Health Analyzer</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #0f172a; color: #e5e7eb; }}
            .card {{ background: #111827; padding: 30px; border-radius: 12px; margin: 20px 0; }}
            h1 {{ color: #60a5fa; text-align: center; }}
            .suggestion {{ background: #0a1224; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #60a5fa; }}
            .button {{ background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Personalized Suggestions</h1>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Age:</strong> {age}</p>
            <p><strong>Mood:</strong> {mood.title()}</p>
            <p><strong>Sleep:</strong> {sleep} hours</p>
            <p><strong>Stress:</strong> {stress}/5</p>
            
            <h2>Suggestions:</h2>
            {''.join([f'<div class="suggestion">{s}</div>' for s in suggestions])}
            
            <a href="/" class="button">Back to Form</a>
        </div>
    </body>
    </html>
    """


@app.route("/test")
def test():
    return "App is working!"


@app.route("/healthz")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
