from app.services.mastery import review_result, supermemo2

def test_failed_review_is_soon():
    days, easiness = supermemo2(1, 3)
    assert days == 1
    assert easiness >= 1.3

def test_passed_review_creates_future_review():
    result = review_result(True, 1, 80)
    assert result.score > 80
    assert result.next_review_at > result.next_review_at.replace(hour=0, minute=0, second=0, microsecond=0)
