from fastapi.testclient import TestClient

# from nask_task_app.app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"task": "nask"}


def test_post_root_empty():
    response = client.post("/")
    assert response.status_code == 404


def test_post_root_invalid():
    response = client.post("/", json={"detail": "invalid"})
    assert response.status_code == 422


def test_post_root_vaid_not_finished():
    response = client.post("/", json={"task": "sleep", "input": 5})
    assert response.status_code == 200
    assert response.json() == {"status": "task not finished"}


def test_post_root_vaid_finished():
    response = client.post("/", json={"task": "sleep", "input": 5})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_:
