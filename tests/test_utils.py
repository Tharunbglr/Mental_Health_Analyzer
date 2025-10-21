from app.utils import score_gad7, score_phq9


def test_score_phq9_minimal_and_suicidal_flag():
    answers = [0, 0, 0, 0, 0, 0, 0, 0, 1]  # last item indicates passive thoughts
    score, level, suicidal = score_phq9(answers)
    assert score == 1
    assert level == "Minimal"
    assert suicidal is True


def test_score_phq9_invalid_length():
    import pytest

    with pytest.raises(ValueError):
        score_phq9([0, 1])


def test_score_gad7_levels():
    assert score_gad7([0] * 7) == (0, "Minimal")
    assert score_gad7([1] * 7) == (7, "Mild")
    assert score_gad7([2] * 7) == (14, "Moderate")
    assert score_gad7([3] * 7) == (21, "Severe")
