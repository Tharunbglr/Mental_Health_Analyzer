def test_index_ok(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Your Well-being Check-in" in res.data


def test_healthz_ok(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_analyze_validation(client):
    res = client.post("/analyze", data={
        "name": "",
        "age": "abc",
        "mood": "",
        "sleep": "-1",
        "stress": "7",
        "thoughts": "",
    })
    assert res.status_code == 200
    assert b"Name is required" in res.data or b"Age must be a number" in res.data


def test_analyze_success(client):
    # include required PHQ-9 (9 items) and GAD-7 (7 items) and lifestyle fields
    data = {
        "name": "Alex",
        "age": "25",
        "mood": "neutral",
        "sleep": "7",
        "stress": "2",
        "thoughts": "Feeling okay",
        "exercise_days": "2",
        "caffeine_cups": "1",
        "screen_hours": "3",
        "support_level": "4",
    }
    # phq9 items (0-3)
    for i in range(1, 10):
        data[f"phq9_{i}"] = "0"
    # gad7 items (0-3)
    for i in range(1, 8):
        data[f"gad7_{i}"] = "0"

    res = client.post("/analyze", data=data)
    assert res.status_code == 200
    assert b"Personalized Suggestions" in res.data


def test_analyze_ai_opt_in(client, monkeypatch):
    # Monkeypatch the ai.generate_ai_feedback to return a predictable string
    from app import ai as ai_module

    def fake_ai(summary):
        return "This is an AI suggestion."

    monkeypatch.setattr(ai_module, "generate_ai_feedback", fake_ai)

    data = {
        "name": "Sam",
        "age": "30",
        "mood": "good",
        "sleep": "7",
        "stress": "2",
        "thoughts": "Doing fine",
        "exercise_days": "3",
        "caffeine_cups": "1",
        "screen_hours": "2",
        "support_level": "4",
        "use_ai": "on",
    }
    for i in range(1, 10):
        data[f"phq9_{i}"] = "0"
    for i in range(1, 8):
        data[f"gad7_{i}"] = "0"

    res = client.post("/analyze", data=data)
    assert res.status_code == 200
    # AI block should be present when generate_ai_feedback returns text
    assert b"AI-assisted insights" in res.data or b"This is an AI suggestion." in res.data


