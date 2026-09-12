from datetime import datetime, timedelta, timezone

from app.models import User
from app.routers.dashboard import level_status
from app.routers.dashboard import learning_path
from app.routers.training import update_streak


def test_level_status_is_independent_per_user():
	assert [level_status(number, 0) for number in range(3)] == ["active", "locked", "locked"]
	assert [level_status(number, 2) for number in range(3)] == ["completed", "completed", "active"]


class PathDb:
	def __init__(self, levels):
		self.path = type("Path", (), {"levels": levels})()

	def scalar(self, query):
		return self.path


def test_two_users_receive_independent_path_statuses():
	levels = [type("Level", (), {"number": number, "status": "locked"})() for number in range(3)]
	first = learning_path(PathDb(levels), User(level=0))
	first_statuses = [level.status for level in first]
	second_levels = [type("Level", (), {"number": number, "status": "locked"})() for number in range(3)]
	second = learning_path(PathDb(second_levels), User(level=2))
	second_statuses = [level.status for level in second]
	assert first_statuses == ["active", "locked", "locked"]
	assert second_statuses == ["completed", "completed", "active"]


def test_streak_increments_same_consecutive_day_and_resets_after_gap():
	first = datetime(2026, 9, 10, 10, tzinfo=timezone.utc)
	user = User(level=0, streak=0)
	update_streak(user, first)
	assert user.streak == 1
	update_streak(user, first.replace(hour=18))
	assert user.streak == 1
	update_streak(user, first + timedelta(days=1))
	assert user.streak == 2
	update_streak(user, first + timedelta(days=3))
	assert user.streak == 1