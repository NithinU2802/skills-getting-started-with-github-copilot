from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = deepcopy(activities)


def reset_activities() -> None:
    activities.clear()
    activities.update(deepcopy(initial_activities))


@pytest.fixture(autouse=True)
def restore_activities():
    reset_activities()
    yield
    reset_activities()


def test_root_redirects_to_static_index_html() -> None:
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activities() -> None:
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert isinstance(response.json(), dict)


def test_signup_for_activity_succeeds_for_new_participant() -> None:
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    expected_message = f"Signed up {new_email} for {activity_name}"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": expected_message}
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_existing_participant_returns_400() -> None:
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404() -> None:
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_succeeds_for_registered_student() -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    expected_message = f"Removed {email} from {activity_name}"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": expected_message}
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404() -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "absentstudent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
