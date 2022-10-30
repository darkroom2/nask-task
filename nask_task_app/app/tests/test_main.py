from unittest import TestCase
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient

from nask_task_app.app.main import app, database, TaskOut


class MockAsyncResult:
    def __init__(self, _id):
        if _id == "TaskGoneInCeleryBackend":
            raise ValueError

    @property
    def status(self):
        return "SUCCESS"

    @property
    def result(self):
        return 5


class TestMain(TestCase):
    client = TestClient(app)

    def tearDown(self):
        database.clear()

    def test_get_root(self):
        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({"task": "nask"}, response.json())

    def test_post_root_notify_empty(self):
        response = self.client.post("/")
        self.assertEqual(422, response.status_code)

    def test_post_root_notify_invalid(self):
        response = self.client.post("/", json={"detail": "invalid"})
        self.assertEqual(422, response.status_code)

    def test_post_root_notify_valid_not_finished(self):
        valid_task = {
            "id": 1,
            "type": "sleep",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/",
            "result": None,
            "status": "PENDING"
        }
        database[valid_task["id"]] = valid_task
        response = self.client.post("/", json=valid_task)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({"status": "task not finished"}, response.json())

    def test_post_root_notify_valid_not_in_db(self):
        valid_task = {
            "id": 1,
            "type": "sleep",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/",
            "result": None,
            "status": "PENDING"
        }
        response = self.client.post("/", json=valid_task)
        self.assertEqual(404, response.status_code)
        self.assertDictEqual({"detail": "task not found"}, response.json())

    def test_post_root_notify_valid_finished(self):
        valid_task = {
            "id": 1,
            "type": "sleep",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/",
            "result": 5,
            "status": "SUCCESS"
        }
        database[valid_task["id"]] = valid_task
        response = self.client.post("/", json=valid_task)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({"status": "ok"}, response.json())

    @patch("nask_task_app.app.main.uuid")
    @patch("nask_task_app.app.main.sleep_task.apply_async")
    def test_task_add_valid_sleep(self, mock_sleep_task, mock_uuid):
        mock_uuid.return_value = "some_uuid"
        mock_sleep_task.return_value = None
        expected_task_detail = {
            "id": "some_uuid",
            "type": "sleep",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/",
            "result": None,
            "status": None
        }
        response = self.client.post("/api/tasks/", json={
            "type": "sleep",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/"
        })
        mock_sleep_task.assert_called_once_with((expected_task_detail,),
                                                task_id="some_uuid")
        self.assertEqual(201, response.status_code)
        self.assertDictEqual(expected_task_detail, response.json())

    @patch("nask_task_app.app.main.uuid")
    @patch("nask_task_app.app.main.prime_task.apply_async")
    def test_task_add_valid_prime(self, mock_sleep_task, mock_uuid):
        mock_uuid.return_value = "some_uuid"
        mock_sleep_task.return_value = None
        expected_task_detail = {
            "id": "some_uuid",
            "type": "prime",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/",
            "result": None,
            "status": None
        }
        response = self.client.post("/api/tasks/", json={
            "type": "prime",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/"
        })
        mock_sleep_task.assert_called_once_with((expected_task_detail,),
                                                task_id="some_uuid")
        self.assertEqual(201, response.status_code)
        self.assertDictEqual(expected_task_detail, response.json())

    @patch("nask_task_app.app.main.uuid")
    @patch("nask_task_app.app.main.fibonacci_task.apply_async")
    def test_task_add_valid_fibonacci(self, mock_sleep_task, mock_uuid):
        mock_uuid.return_value = "some_uuid"
        mock_sleep_task.return_value = None
        expected_task_detail = {
            "id": "some_uuid",
            "type": "fibonacci",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/",
            "result": None,
            "status": None
        }
        response = self.client.post("/api/tasks/", json={
            "type": "fibonacci",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/"
        })
        mock_sleep_task.assert_called_once_with((expected_task_detail,),
                                                task_id="some_uuid")
        self.assertEqual(201, response.status_code)
        self.assertDictEqual(expected_task_detail, response.json())

    def test_task_add_invalid(self):
        response = self.client.post("/api/tasks/", json={
            "type": "workout",
            "payload": {"input": "deadlift"},
            "notify_url": "http://localhost:8000/"
        })
        self.assertEqual(422, response.status_code)

    def test_get_task_statuses_empty(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual({"tasks": []}, response.json())

    def test_get_task_statuses_not_empty(self):
        database["some_uuid"] = {
            "id": "some_uuid",
            "type": "sleep",
            "payload": {"input": 5},
            "notify_url": "http://localhost:8000/",
            "result": None,
            "status": None
        }
        expected_task_statuses = {"tasks": [database["some_uuid"]]}
        response = self.client.get("/api/tasks/")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_task_statuses, response.json())

    @patch("nask_task_app.app.main.AsyncResult",
           Mock(side_effect=MockAsyncResult))
    def test_get_task_status_detail_valid(self):
        database["some_uuid"] = TaskOut(
            id="some_uuid",
            type="sleep",
            payload={"input": 5},
            notify_url="http://localhost:8000/",
            result=None,
            status=None
        )
        response = self.client.get("/api/tasks/some_uuid")
        # database update should happen after calling the endpoint
        expected_task_detail = database["some_uuid"]
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_task_detail.dict(), response.json())

    @patch("nask_task_app.app.main.AsyncResult",
           Mock(side_effect=MockAsyncResult))
    def test_get_task_status_detail_valid_celery_error(self):
        database["TaskGoneInCeleryBackend"] = TaskOut(
            id="TaskGoneInCeleryBackend",
            type="prime",
            payload={"input": 5},
            notify_url="http://localhost:8000/",
            result=None,
            status=None
        )
        response = self.client.get("/api/tasks/TaskGoneInCeleryBackend")
        self.assertEqual(500, response.status_code)
        self.assertDictEqual(
            {"detail": "error with task: TaskGoneInCeleryBackend"},
            response.json()
        )

    def test_get_task_status_detail_not_found(self):
        response = self.client.get("/api/tasks/some_uuid")
        self.assertEqual(404, response.status_code)
