"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    original_state = {name: {"participants": list(info["participants"])} for name, info in activities.items()}
    yield
    for name, info in activities.items():
        if name in original_state:
            info["participants"] = original_state[name]["participants"]


class TestGetActivities:
    def test_get_activities_returns_200(self):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)

    def test_get_activities_has_expected_fields(self):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        first_activity = next(iter(data.values()))

        # Assert
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity


class TestSignupForActivity:
    def test_signup_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_adds_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        activities_response = client.get("/activities")
        data = activities_response.json()

        # Assert
        assert email in data[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_unknown_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404


class TestUnregisterFromActivity:
    def test_unregister_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_unregister_removes_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        activities_response = client.get("/activities")
        data = activities_response.json()

        # Assert
        assert email not in data[activity_name]["participants"]

    def test_unregister_not_signed_up_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400

    def test_unregister_unknown_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
