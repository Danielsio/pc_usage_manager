import pytest
from django.contrib.auth.models import User
from time_management.models import UserTime

@pytest.mark.django_db
def test_user_time_creation_signal():
    user = User.objects.create_user(username='testuser', password='password123')

    user_time = UserTime.objects.get(user=user)
    assert user_time is not None
    assert user_time.remaining_time.total_seconds() == 0

@pytest.mark.django_db
def test_user_time_update_signal():
    user = User.objects.create_user(username='testuser', password='password123')

    user_time = user.time
    user_time.add_time(30)
    assert user_time.remaining_time.total_seconds() == 1800

    user_time.reduce_time(15)
    assert user_time.remaining_time.total_seconds() == 900
