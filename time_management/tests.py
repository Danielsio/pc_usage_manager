import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from time_management.models import UserTime

DEFAULT_USERNAME = "testuser"
DEFAULT_EMAIL = "user@example.com"
DEFAULT_PASSWORD = "password123"

@pytest.fixture
def api_client():
    """Fixture for DRF's API client."""
    return APIClient()


@pytest.fixture
def user():
    """Fixture to create a default user."""
    return User.objects.create_user(username=DEFAULT_USERNAME, email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD)


def obtain_tokens(api_client, username, password):
    """Helper to obtain authentication tokens."""
    url = reverse("login")
    data = {"username": username, "password": password}
    response = api_client.post(url, data, format="json")
    if response.status_code == status.HTTP_200_OK:
        return response.data.get("access"), response.data.get("refresh")
    return None, None


def refresh_access_token(api_client, refresh_token):
    """Helper to refresh the access token."""
    url = reverse("token_refresh")
    data = {"refresh": refresh_token}
    response = api_client.post(url, data, format="json")
    if response.status_code == status.HTTP_200_OK:
        return response.data.get("access")
    return None


@pytest.mark.django_db
def test_user_registration(api_client):
    """Test user registration endpoint."""
    url = reverse('register')
    data = {
        "username": DEFAULT_USERNAME,
        "email": DEFAULT_EMAIL,
        "password": DEFAULT_PASSWORD
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username=DEFAULT_USERNAME).exists()


@pytest.mark.django_db
def test_add_time(api_client, user):
    """Test adding time to a user's remaining time."""
    access_token, refresh_token = obtain_tokens(api_client, DEFAULT_USERNAME, DEFAULT_PASSWORD)
    url = reverse('user-time', kwargs={"username": user.username})
    data = {"add_minutes": 15}
    headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}
    response = api_client.patch(url, data, format='json', **headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["remaining_time"] == "00:15:00"  # 15 minutes added


@pytest.mark.django_db
def test_add_time_no_auth(api_client, user):
    """Test adding time to a user's remaining time without authentication."""
    url = reverse('user-time', kwargs={"username": user.username})
    data = {"add_minutes": 15}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data.get("detail") == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_update_time(api_client, user):
    """Test updating a user's remaining time."""
    access_token, refresh_token = obtain_tokens(api_client, DEFAULT_USERNAME, DEFAULT_PASSWORD)
    url = reverse('update-user-time', kwargs={"username": user.username})

    # Send remaining_time in seconds (45 minutes = 2700 seconds)
    data = {"remaining_time": 2700}
    headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}
    response = api_client.patch(url, data, format='json', **headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["remaining_time"] == "00:45:00"


@pytest.mark.django_db
def test_update_time_no_auth(api_client, user):
    """Test updating a user's remaining time without authentication."""
    url = reverse('update-user-time', kwargs={"username": user.username})

    # Send remaining_time in seconds (45 minutes = 2700 seconds)
    data = {"remaining_time": 2700}
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data.get("detail") == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_login_success(api_client):
    """Test successful login."""
    url = reverse("login")
    data = {"username": DEFAULT_USERNAME, "password": DEFAULT_PASSWORD}
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data["username"] == DEFAULT_USERNAME


@pytest.mark.django_db
def test_login_failure_invalid_password(api_client):
    """Test login failure due to invalid credentials."""
    url = reverse("login")
    data = {"username": DEFAULT_USERNAME, "password": "wrongpassword"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"] == "Invalid username or password."


@pytest.mark.django_db
def test_login_failure_not_existing_username(api_client):
    """Test login failure due to invalid credentials."""
    url = reverse("login")
    data = {"username": "non_existing", "password": DEFAULT_PASSWORD}
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"] == "Invalid username or password."


@pytest.mark.django_db
def test_login_failure_missing_fields(api_client):
    """Test login failure due to missing username or password."""
    url = reverse("login")

    # Missing both fields
    response = api_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Both username and password are required."

    # Missing password
    response = api_client.post(url, {"username": "testuser"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Both username and password are required."

    # Missing username
    response = api_client.post(url, {"password": "password123"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Both username and password are required."


@pytest.mark.django_db
def test_user_time_creation_signal(user):
    user_time = UserTime.objects.get(user=user)
    assert user_time is not None
    assert user_time.remaining_time.total_seconds() == 0

@pytest.mark.django_db
def test_user_time_add_signal(user):
    user_time = user.time
    user_time.add_time(30)
    assert user_time.remaining_time.total_seconds() == 1800
