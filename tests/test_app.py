from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_and_appears_in_list():
    activity = "Basketball Team"
    email = "tester@example.com"

    # Ensure starting state: remove if already present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    url = f"/activities/{quote(activity)}/signup"
    res = client.post(url, params={"email": email})
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")

    # Appears in GET /activities
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert email in data[activity]["participants"]

    # Duplicate signup should fail
    res = client.post(url, params={"email": email})
    assert res.status_code == 400


def test_unregister_participant():
    activity = "Basketball Team"
    email = "remove-me@example.com"

    # Make sure participant exists
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    url = f"/activities/{quote(activity)}/participants"
    res = client.delete(url, params={"email": email})
    assert res.status_code == 200
    assert "Unregistered" in res.json().get("message", "")

    # Now deleting again returns 404
    res = client.delete(url, params={"email": email})
    assert res.status_code == 404
