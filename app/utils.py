"""Utility helpers for scoring PHQ-9 and GAD-7 and interpreting results.

These functions centralize the scoring rules so tests can validate behavior
and the routes can remain concise.
"""
from typing import List, Tuple


def score_phq9(answers: List[int]) -> Tuple[int, str, bool]:
    """Compute PHQ-9 score and severity level.

    Returns (score, level_label, suicidal_item_flag).
    - answers: list of 9 integers (0-3)
    - suicidal_item_flag: True if item 9 (index 8) >= 1
    """
    if len(answers) != 9:
        raise ValueError("PHQ-9 requires 9 answers")
    score = sum(int(x) for x in answers)
    suicidal_flag = int(answers[8]) >= 1
    if score <= 4:
        level = "Minimal"
    elif score <= 9:
        level = "Mild"
    elif score <= 14:
        level = "Moderate"
    elif score <= 19:
        level = "Moderately severe"
    else:
        level = "Severe"
    return score, level, suicidal_flag


def score_gad7(answers: List[int]) -> Tuple[int, str]:
    """Compute GAD-7 score and severity level.

    Returns (score, level_label).
    - answers: list of 7 integers (0-3)
    """
    if len(answers) != 7:
        raise ValueError("GAD-7 requires 7 answers")
    score = sum(int(x) for x in answers)
    if score <= 4:
        level = "Minimal"
    elif score <= 9:
        level = "Mild"
    elif score <= 14:
        level = "Moderate"
    else:
        level = "Severe"
    return score, level
