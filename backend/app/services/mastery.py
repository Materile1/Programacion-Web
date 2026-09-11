from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

@dataclass
class MasteryResult:
    score: float
    quality: float
    interval_days: int
    next_review_at: datetime
    label: str

LABELS = [(20, "🔵 Dominado"), (12, "🟢 Sólido"), (6, "🟡 En progreso"), (0, "🟠 Reforzar")]

def evaluate_quality(passed: bool, test_ratio: float, code_length: int) -> float:
    quality = (4.0 if passed else 1.5) + min(test_ratio, 1.0) * 1.3
    if 20 <= code_length <= 400:
        quality += 0.7
    return max(0.0, min(5.0, quality))

def supermemo2(quality: float, repetitions: int = 0, easiness: float = 2.5) -> tuple[int, float]:
    if quality < 3:
        return 1, max(1.3, easiness - 0.2)
    if repetitions == 0:
        return 1, easiness
    if repetitions == 1:
        return 6, easiness
    new_easiness = max(1.3, easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return max(1, round(repetitions * new_easiness)), new_easiness

def mastery_from_score(score: float) -> str:
    for threshold, label in LABELS:
        if score >= threshold:
            return label
    return "🔴 Recién iniciado"

def review_result(passed: bool, test_ratio: float, code_length: int, repetitions: int = 0) -> MasteryResult:
    quality = evaluate_quality(passed, test_ratio, code_length)
    interval, _ = supermemo2(quality, repetitions)
    score = quality / 5 * 100
    return MasteryResult(score, quality, interval, datetime.now(timezone.utc) + timedelta(days=interval), mastery_from_score(score))
