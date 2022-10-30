from enum import Enum
from os import environ
from uuid import UUID

from celery import Celery
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException, Path
from kombu import uuid
from pydantic import BaseModel, AnyHttpUrl


class TaskType(str, Enum):
    SLEEP = "sleep"
    PRIME = "prime"
    FIBONACCI = "fibonacci"


class TaskPayload(BaseModel):
    input: int


class TaskIn(BaseModel):
    type: TaskType
    notify_url: AnyHttpUrl
    payload: TaskPayload


class TaskOut(TaskIn):  # TODO: remove extra fields in README.md
    id: int | str | UUID | None
    status: str | None
    result: int | bool | None


class TaskList(BaseModel):
    tasks: list[TaskOut]


database = {}

app = FastAPI()

celery = Celery(__name__,
                broker=environ.get("CELERY_BROKER_URL"),
                backend=environ.get("CELERY_BACKEND_URL"))


@celery.task
def notify_task(task_details: dict) -> dict:
    import requests
    task_result = AsyncResult(task_details["id"])
    while not task_result.ready():
        continue
    task_details["status"] = task_result.status
    task_details["result"] = task_result.result
    try:
        connect_timeout, read_timeout = 5.0, 30.0
        response = requests.post(task_details["notify_url"],
                                 json=task_details,
                                 timeout=(connect_timeout, read_timeout))
    except requests.RequestException:
        return {"status": "error", "message": "notify failed"}
    return response.json()


@celery.task
def sleep_task(task_details: dict) -> int:
    import time
    seconds = task_details["payload"]["input"]
    time.sleep(seconds)
    notify_task.delay(task_details)
    return seconds


@celery.task
def prime_task(task_details: dict) -> bool:
    n = task_details["payload"]["input"]
    if n < 2:
        notify_task.delay(task_details)
        return False
    for i in range(2, n):
        if n % i == 0:
            notify_task.delay(task_details)
            return False
    notify_task.delay(task_details)
    return True


@celery.task
def fibonacci_task(task_details: dict) -> int:

    def fib(n: int) -> int:
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)

    _n = task_details["payload"]["input"]
    result = fib(_n)
    notify_task.delay(task_details)
    return result


@app.get("/")
async def root():
    return {"task": "nask"}


@app.post("/")
async def root_notify(task_details: TaskOut):
    if task_details.id in database:
        database[task_details.id] = task_details
        if not task_details.status == "SUCCESS":
            return {"status": "task not finished"}
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="task not found")


@app.get("/api/tasks/", response_model=TaskList)
async def tasks_statuses():
    return {"tasks": [task for task in database.values()]}


@app.get("/api/tasks/{_uuid}", response_model=TaskOut)
async def task_status(_uuid: int | str | UUID = Path(..., title="task UUID")):
    if _uuid in database:
        task_details = database[_uuid]
        try:
            task_result = AsyncResult(task_details.id)
            task_details.status = task_result.status
            task_details.result = task_result.result
            database[_uuid] = task_details
            return task_details
        except ValueError as e:
            raise HTTPException(status_code=500,
                                detail=f"error with task: {_uuid}") from e
    raise HTTPException(status_code=404,
                        detail=f"task with id: {_uuid} not found")


@app.post("/api/tasks/", response_model=TaskOut, status_code=201)
async def task_add(task_in: TaskIn):
    # Create task out object
    task_out = TaskOut(**task_in.dict(), id=uuid())
    # Check task type and add to queue
    if task_in.type == TaskType.SLEEP:
        task = sleep_task
    elif task_in.type == TaskType.PRIME:
        task = prime_task
    else:
        task = fibonacci_task
    task.apply_async((task_out.dict(),), task_id=task_out.id)
    # Add task to database
    database[task_out.id] = task_out
    # Return task
    return task_out
