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


def test_score_phq9_all_levels():
    """Test all PHQ-9 severity levels"""
    # Minimal: 0-4
    assert score_phq9([0] * 9)[1] == "Minimal"
    assert score_phq9([0, 0, 1, 1, 0, 0, 0, 0, 0])[1] == "Minimal"
    # Mild: 5-9
    assert score_phq9([1] * 9)[1] == "Mild"
    # Moderate: 10-14
    mild_answers = [2, 2, 1, 1, 1, 1, 1, 1, 0]
    assert score_phq9(mild_answers)[1] == "Moderate"
    # Moderately Severe: 15-19
    mod_severe = [2, 2, 2, 2, 2, 2, 2, 1, 0]
    assert score_phq9(mod_severe)[1] == "Moderately Severe"
    # Severe: 20-27
    assert score_phq9([3] * 9)[1] == "Severe"


def test_score_gad7_invalid_length():
    """Test GAD-7 validation of input length"""
    import pytest
    with pytest.raises(ValueError):
        score_gad7([1, 2, 3])  # Too short
    with pytest.raises(ValueError):
        score_gad7([1, 1, 1, 1, 1, 1, 1, 1])  # Too long


def test_score_gad7_boundary_cases():
    """Test GAD-7 scoring at level boundaries"""
    # Test minimal-mild boundary (4-5)
    assert score_gad7([1, 1, 1, 1, 0, 0, 0])[1] == "Minimal"  # Score: 4
    assert score_gad7([1, 1, 1, 1, 1, 0, 0])[1] == "Mild"    # Score: 5
    
    # Test mild-moderate boundary (9-10)
    assert score_gad7([2, 1, 1, 1, 1, 1, 1])[1] == "Mild"     # Score: 9
    assert score_gad7([2, 2, 1, 1, 1, 1, 1])[1] == "Moderate" # Score: 10
    
    # Test moderate-severe boundary (14-15)
    assert score_gad7([2, 2, 2, 2, 2, 2, 2])[1] == "Moderate" # Score: 14
    assert score_gad7([3, 2, 2, 2, 2, 2, 2])[1] == "Severe"   # Score: 15
