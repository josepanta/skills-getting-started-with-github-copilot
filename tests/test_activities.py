from fastapi.testclient import TestClient
from src.app import app, activities
import copy

client = TestClient(app)

# Save original activities to restore state after tests
_original_activities = copy.deepcopy(activities)


def setup_function():
    # Before each test, reset activities to original state
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def teardown_function():
    # After each test, reset activities to original state
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_get_activities_returns_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_delete_participant():
    email = "testuser@mergington.edu"
    activity = "Chess Club"

    # Ensure not already in participants
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert f"Signed up {email} for {activity}" in resp.json().get("message", "")

    # Verify participant added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Delete participant
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert f"Unregistered {email} from {activity}" in resp.json().get("message", "")

    # Verify removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_duplicate_signup_fails():
    activity = "Programming Class"
    email = "emma@mergington.edu"  # already signed up in initial data

    # Try to sign up same email again
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400


def test_delete_nonexistent_participant_returns_404():
    activity = "Programming Class"
    email = "nonexistent@mergington.edu"

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404


def test_signup_nonexistent_activity_returns_404():
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 404


def test_delete_nonexistent_activity_returns_404():
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
