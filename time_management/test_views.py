import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import timedelta
from rest_framework.test import APIClient
from time_management.models import UserTime


# Fixtures
@pytest.fixture
def api_client():
    """Fixture for DRF's API client."""
    return APIClient()


@pytest.fixture
def create_user():
    """Fixture to create a user."""
    def _create_user(username, email="user@example.com", password="password123"):
        return User.objects.create_user(username=username, email=email, password=password)
    return _create_user


@pytest.fixture
def create_user_with_time(create_user):
    """Fixture to create a user with default remaining time."""
    def _create_user_with_time(username, email="user@example.com", password="password123"):
        user = create_user(username, email, password)
        user_time = UserTime.objects.get(user=user)  # Automatically created by signal
        return user, user_time
    return _create_user_with_time


# Helper Functions
def perform_get_user_time(api_client, username):
    """Helper to perform a GET request for user time."""
    url = reverse('user-time', kwargs={"username": username})
    return api_client.get(url)


def perform_patch_user_time(api_client, username, data):
    """Helper to perform a PATCH request for user time."""
    url = reverse('user-time', kwargs={"username": username})
    return api_client.patch(url, data, format='json')


# Tests
@pytest.mark.django_db
def test_user_registration(api_client):
    """Test user registration endpoint."""
    url = reverse('register')
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_get_user_time(api_client, create_user_with_time):
    """Test retrieving user's remaining time."""
    user, _ = create_user_with_time("testuser")
    response = perform_get_user_time(api_client, user.username)
    assert response.status_code == 200
    assert response.data["user"] == "testuser"
    assert response.data["remaining_time"] == "00:00:00"


@pytest.mark.django_db
def test_add_time(api_client, create_user_with_time):
    """Test adding time to a user's remaining time."""
    user, _ = create_user_with_time("testuser")
    data = {"add_minutes": 15}
    response = perform_patch_user_time(api_client, user.username, data)
    assert response.status_code == 200
    assert response.data["remaining_time"] == "00:15:00"  # 15 minutes added


@pytest.mark.django_db
def test_update_time(api_client, create_user_with_time):
    """Test updating a user's remaining time."""
    user, _ = create_user_with_time("testuser")
    url = reverse('update-user-time', kwargs={"username": user.username})

    # Send remaining_time in seconds (45 minutes = 2700 seconds)
    data = {"remaining_time": 2700}
    response = api_client.patch(url, data, format='json')

    assert response.status_code == 200
    assert response.data["remaining_time"] == "00:45:00"


@pytest.mark.django_db
def test_get_nonexistent_user_time(api_client):
    """Test retrieving time for a non-existent user."""
    response = perform_get_user_time(api_client, "nonexistentuser")
    assert response.status_code == 404
    assert response.data["error"] == "User or time not found"
