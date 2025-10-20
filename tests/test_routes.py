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
    res = client.post("/analyze", data={
        "name": "Alex",
        "age": "25",
        "mood": "neutral",
        "sleep": "7",
        "stress": "2",
        "thoughts": "Feeling okay",
    })
    assert res.status_code == 200
    assert b"Personalized Suggestions" in res.data


