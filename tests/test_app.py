import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI app."""
    return TestClient(app)


class TestRootEndpoint:
    def test_get_root_redirects_to_static_index(self, client):
        # Arrange: Set up the test client

        # Act: Make a GET request to the root endpoint
        response = client.get("/")

        # Assert: Verify the response is a redirect to /static/index.html
        assert response.status_code == 200  # TestClient follows redirects by default
        # The content should be the static file, but since it's mounted, we check URL
        assert response.url.path == "/static/index.html"


class TestActivitiesEndpoint:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange: Set up the test client

        # Act: Make a GET request to /activities
        response = client.get("/activities")

        # Assert: Verify the response status and structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        # Verify structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    def test_signup_successful_for_valid_activity_and_email(self, client):
        # Arrange: Set up test data
        activity_name = "Chess Club"
        email = "test@example.com"

        # Act: Make a POST request to signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Verify successful signup
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity_name}" in data["message"]

    def test_signup_fails_for_nonexistent_activity(self, client):
        # Arrange: Set up test data with invalid activity
        activity_name = "Nonexistent Activity"
        email = "test@example.com"

        # Act: Make a POST request to signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_fails_for_duplicate_email(self, client):
        # Arrange: Set up test data and sign up once
        activity_name = "Programming Class"
        email = "duplicate@example.com"
        client.post(f"/activities/{activity_name}/signup?email={email}")  # First signup

        # Act: Attempt to sign up again
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Verify 400 error for duplicate
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up" in data["detail"]


class TestUnregisterEndpoint:
    def test_unregister_successful_for_registered_participant(self, client):
        # Arrange: Set up test data and sign up first
        activity_name = "Gym Class"
        email = "unregister@example.com"
        client.post(f"/activities/{activity_name}/signup?email={email}")  # Signup first

        # Act: Make a DELETE request to unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert: Verify successful unregister
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Unregistered {email} from {activity_name}" in data["message"]

    def test_unregister_fails_for_nonexistent_activity(self, client):
        # Arrange: Set up test data with invalid activity
        activity_name = "Nonexistent Activity"
        email = "test@example.com"

        # Act: Make a DELETE request to unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_fails_for_unregistered_participant(self, client):
        # Arrange: Set up test data
        activity_name = "Basketball Team"
        email = "notregistered@example.com"

        # Act: Make a DELETE request to unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Student not registered" in data["detail"]


class TestEdgeCases:
    def test_signup_with_empty_email(self, client):
        # Arrange: Set up test data with empty email
        activity_name = "Tennis Club"
        email = ""

        # Act: Make a POST request to signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Verify it succeeds (no validation in app)
        assert response.status_code == 200

    def test_signup_with_special_characters_in_activity_name(self, client):
        # Arrange: Set up test data with special chars (but activity doesn't exist)
        activity_name = "Test%20Activity"
        email = "test@example.com"

        # Act: Make a POST request to signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Verify 404 for non-existent activity
        assert response.status_code == 404

    def test_get_activities_structure(self, client):
        # Arrange: Set up the test client

        # Act: Make a GET request to /activities
        response = client.get("/activities")

        # Assert: Verify detailed structure
        assert response.status_code == 200
        data = response.json()
        for activity_name, details in data.items():
            assert isinstance(details, dict)
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)
            assert isinstance(details["max_participants"], int)