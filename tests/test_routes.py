def test_index_ok(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Your Well-being Check-in" in res.data


def test_healthz_ok(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_404_page(client):
    """Test custom 404 error page"""
    res = client.get("/nonexistent-page")
    assert res.status_code == 404
    assert b"Page not found" in res.data
    assert b"The page you are looking for does not exist" in res.data
    # Should have crisis resources even on error page
    assert b"Crisis Support" in res.data


def test_405_method_not_allowed(client):
    """Test method not allowed errors"""
    res = client.get("/analyze")  # Should be POST only
    assert res.status_code == 405


def test_500_error_page(app, client):
    """Test custom 500 error page"""
    # Register error handlers
    from app.health import register_error_handlers
    register_error_handlers(app)

    with app.test_request_context():
        from flask import abort
        @app.route("/error-test")
        def error_test():
            abort(500)

        res = client.get("/error-test")
        assert res.status_code == 500
        assert b"Something went wrong" in res.data
        assert b"We encountered an unexpected error" in res.data
        # Should have crisis resources even on error page
        assert b"Crisis Support" in res.data


def test_analyze_validation(client):
    res = client.post(
        "/analyze",
        data={
            "name": "",
            "age": "abc",
            "mood": "",
            "sleep": "-1",
            "stress": "7",
            "thoughts": "",
        },
    )
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


def test_privacy_page(client):
    res = client.get("/privacy")
    assert res.status_code == 200
    assert b"Privacy Policy" in res.data
    assert b"Information We Collect" in res.data


def test_terms_page(client):
    res = client.get("/terms")
    assert res.status_code == 200
    assert b"Terms of Service" in res.data
    assert b"Important Disclaimers" in res.data


def test_analyze_high_risk_response(client):
    """Test that high-risk responses trigger appropriate warnings"""
    data = {
        "name": "Sam",
        "age": "25",
        "mood": "very low",
        "sleep": "7",
        "stress": "5",
        "thoughts": "feeling hopeless",
        "exercise_days": "2",
        "caffeine_cups": "1",
        "screen_hours": "3",
        "support_level": "1",
    }
    # High PHQ-9 scores including suicidal ideation
    for i in range(1, 9):
        data[f"phq9_{i}"] = "3"
    data["phq9_9"] = "3"  # Suicidal ideation question
    # High GAD-7 scores
    for i in range(1, 8):
        data[f"gad7_{i}"] = "3"

    res = client.post("/analyze", data=data)
    assert res.status_code == 200
    # Should see crisis resources and warnings
    assert b"seek immediate help" in res.data.lower()
    assert b"crisis" in res.data.lower()
    assert b"988" in res.data  # Crisis hotline


def test_analyze_lifestyle_suggestions(client):
    """Test that lifestyle inputs generate appropriate suggestions"""
    data = {
        "name": "Alex",
        "age": "30",
        "mood": "neutral",
        "sleep": "7",
        "stress": "3",
        "thoughts": "normal day",
        "exercise_days": "0",  # No exercise
        "caffeine_cups": "5",  # High caffeine
        "screen_hours": "10",  # High screen time
        "support_level": "2",  # Low support
    }
    # Normal PHQ-9 and GAD-7 scores
    for i in range(1, 10):
        data[f"phq9_{i}"] = "0"
    for i in range(1, 8):
        data[f"gad7_{i}"] = "0"

    res = client.post("/analyze", data=data)
    assert res.status_code == 200
    # Should see lifestyle-related suggestions
    assert b"exercise" in res.data.lower()
    assert b"caffeine" in res.data.lower()
    assert b"screen" in res.data.lower()
    assert b"support" in res.data.lower()


def test_analyze_boundary_cases(client):
    """Test edge cases in form validation"""
    # Test age boundaries
    data = {
        "name": "Test",
        "age": "12",  # Below minimum age
        "mood": "neutral",
        "sleep": "7",
        "stress": "3",
        "thoughts": "normal",
        "exercise_days": "2",
        "caffeine_cups": "1",
        "screen_hours": "3",
        "support_level": "3",
    }
    for i in range(1, 10):
        data[f"phq9_{i}"] = "0"
    for i in range(1, 8):
        data[f"gad7_{i}"] = "0"

    res = client.post("/analyze", data=data)
    assert b"Enter a realistic age" in res.data

    # Test sleep hours boundary
    data["age"] = "25"
    data["sleep"] = "25"  # Above max hours
    res = client.post("/analyze", data=data)
    assert b"Enter hours between 0 and 24" in res.data

    # Test missing questionnaire answers
    del data["phq9_1"]
    data["sleep"] = "7"
    res = client.post("/analyze", data=data)
    assert b"Select 0-3" in res.data


def test_analyze_xss_prevention(client):
    """Test that user input is properly escaped in output"""
    data = {
        "name": "<script>alert('xss')</script>",
        "age": "25",
        "mood": "neutral",
        "sleep": "7",
        "stress": "3",
        "thoughts": "<img src=x onerror=alert('xss')>",
        "exercise_days": "2",
        "caffeine_cups": "1",
        "screen_hours": "3",
        "support_level": "3",
    }
    for i in range(1, 10):
        data[f"phq9_{i}"] = "0"
    for i in range(1, 8):
        data[f"gad7_{i}"] = "0"

    res = client.post("/analyze", data=data)
    assert res.status_code == 200
    # Script tags should be escaped
    assert b"<script>" not in res.data
    assert b"&lt;script&gt;" in res.data
    assert b"<img src=x" not in res.data


def test_analyze_special_characters(client):
    """Test handling of special characters and Unicode in input"""
    data = {
        "name": "María José",  # Unicode name
        "age": "25",
        "mood": "neutral",
        "sleep": "7",
        "stress": "3",
        "thoughts": "Everything's fine! (test punctuation: @#$%)",
        "exercise_days": "2",
        "caffeine_cups": "1",
        "screen_hours": "3",
        "support_level": "3",
    }
    for i in range(1, 10):
        data[f"phq9_{i}"] = "0"
    for i in range(1, 8):
        data[f"gad7_{i}"] = "0"

    res = client.post("/analyze", data=data)
    assert res.status_code == 200
    # Unicode and special characters should be preserved
    assert "María José".encode() in res.data
    assert b"@#$%" in res.data


def test_analyze_concurrent_requests(client):
    """Test handling multiple requests concurrently"""
    import concurrent.futures

    def make_request():
        data = {
            "name": "Test",
            "age": "25",
            "mood": "neutral",
            "sleep": "7",
            "stress": "3",
            "thoughts": "normal",
            "exercise_days": "2",
            "caffeine_cups": "1",
            "screen_hours": "3",
            "support_level": "3",
            "use_ai": "on",
        }
        for i in range(1, 10):
            data[f"phq9_{i}"] = "0"
        for i in range(1, 8):
            data[f"gad7_{i}"] = "0"
        return client.post("/analyze", data=data)

    # Make 5 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(5)]
        responses = [f.result() for f in futures]

    # All requests should succeed
    for res in responses:
        assert res.status_code == 200
        assert b"Personalized Suggestions" in res.data
