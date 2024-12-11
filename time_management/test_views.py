import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from time_management.models import UserTime

DEFAULT_USERNAME = "testuser"
DEFAULT_EMAIL = "user@example.com"
DEFAULT_PASSWORD = "password123"

# Fixtures
@pytest.fixture
def api_client():
    """Fixture for DRF's API client."""
    return APIClient()


@pytest.fixture
def user():
    """Fixture to create a default user."""
    return User.objects.create_user(username=DEFAULT_USERNAME, email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD)


def perform_get_user_time(api_client, username, auth=False):
    """Helper to perform a GET request for user time."""
    url = reverse('user-time', kwargs={"username": username})
    if auth:
        # Attempt login and check success
        login_response = api_client.login(username=username, password=DEFAULT_PASSWORD)
        if not login_response:  # If login failed, return an error-like response or raise an exception
            return {"error": "Authentication failed. Please check credentials."}
    return api_client.get(url)


def perform_patch_user_time(api_client, username, data, auth=False):
    """Helper to perform a PATCH request for user time."""
    url = reverse('user-time', kwargs={"username": username})
    if auth:
        # Attempt login and check success
        login_response = api_client.login(username=username, password=DEFAULT_PASSWORD)
        if not login_response:  # If login failed, return an error-like response or raise an exception
            return {"error": "Authentication failed. Please check credentials."}
    return api_client.patch(url, data, format='json')


# Tests
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
def test_get_user_time(api_client, user):
    """Test retrieving user's remaining time."""
    # Authenticate before fetching
    response = perform_get_user_time(api_client, user.username, auth=True)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["user"] == "testuser"
    assert response.data["remaining_time"] == "00:00:00"

@pytest.mark.django_db
def test_get_user_time_no_auth(api_client, user):
    """Test retrieving user's remaining time without authentication."""
    # Attempt to fetch without authentication
    response = perform_get_user_time(api_client, user.username, auth=False)

    # Assert that the response is unauthorized
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data.get("detail") == "Authentication credentials were not provided."

@pytest.mark.django_db
def test_add_time(api_client, user):
    """Test adding time to a user's remaining time."""
    data = {"add_minutes": 15}
    response = perform_patch_user_time(api_client, user.username, data, auth=True)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["remaining_time"] == "00:15:00"  # 15 minutes added

@pytest.mark.django_db
def test_add_time_no_auth(api_client, user):
    """Test adding time to a user's remaining time."""
    data = {"add_minutes": 15}
    response = perform_patch_user_time(api_client, user.username, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data.get("detail") == "Authentication credentials were not provided."

@pytest.mark.django_db
def test_update_time(api_client, user):
    """Test updating a user's remaining time."""
    url = reverse('update-user-time', kwargs={"username": user.username})

    # Send remaining_time in seconds (45 minutes = 2700 seconds)
    data = {"remaining_time": 2700}
    api_client.login(username=user.username, password=DEFAULT_PASSWORD)
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["remaining_time"] == "00:45:00"

@pytest.mark.django_db
def test_update_time_no_auth(api_client, user):
    """Test updating a user's remaining time."""
    url = reverse('update-user-time', kwargs={"username": user.username})

    # Send remaining_time in seconds (45 minutes = 2700 seconds)
    data = {"remaining_time": 2700}
    api_client.login()
    response = api_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data.get("detail") == "Authentication credentials were not provided."

@pytest.mark.django_db
def test_login_success(api_client, user):
    """Test successful login."""

    url = reverse("login")
    data = {"username": DEFAULT_USERNAME, "password": DEFAULT_PASSWORD}
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert response.data["username"] == DEFAULT_USERNAME
    assert "remaining_time" in response.data


@pytest.mark.django_db
def test_login_failure_invalid_password(api_client, user):
    """Test login failure due to invalid credentials."""

    url = reverse("login")
    data = {"username": DEFAULT_USERNAME, "password": "wrongpassword"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"] == "Invalid username or password."

@pytest.mark.django_db
def test_login_failure_not_existing_username(api_client, user):
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