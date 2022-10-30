from enum import Enum
from os import environ, getcwd  # TODO: remove cwd
from uuid import UUID

from celery import Celery
from celery.result import AsyncResult
from dotenv import load_dotenv  # TODO: remove
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, HttpUrl


class TaskType(str, Enum):
    sleep = "sleep"
    prime = "prime"
    fibonacci = "fibonacci"


class TaskPayload(BaseModel):
    input: int


class TaskIn(BaseModel):
    type: TaskType
    notify_url: HttpUrl
    payload: TaskPayload


class TaskOut(TaskIn):  # TODO: remove extra fields in README.md
    id: int | str | UUID | None
    status: str | None
    result: int | bool | None


class TaskList(BaseModel):
    tasks: list[TaskOut]


database = {
    1: TaskOut(id=1, type=TaskType.sleep, status="PENDING",
               notify_url="http://127.0.0.1:8000/",
               payload=TaskPayload(input=5)),
    2: TaskOut(id=2, type=TaskType.prime, status="STARTED",
               notify_url="http://127.0.0.1:8000/",
               payload=TaskPayload(input=10)),
    3: TaskOut(id=3, type=TaskType.fibonacci, status="SUCCESS",
               notify_url="http://127.0.0.1:8000/",
               payload=TaskPayload(input=101))
}

app = FastAPI()

load_dotenv(getcwd() + '/.envs/.dev')  # TODO: remove

celery = Celery(
    __name__,
    broker=environ.get("CELERY_BROKER_URL"),
    backend=environ.get("CELERY_BACKEND_URL")
)


@celery.task
def notify_task(task_details: TaskOut) -> bool:
    import requests
    task_result = AsyncResult(task_details.id).get()
    task_details.status = task_result.status
    task_details.result = task_result.result
    try:
        connect_timeout, read_timeout = 5.0, 30.0
        requests.post(task_details.notify_url, json=task_details,
                      timeout=(connect_timeout, read_timeout))
    except requests.RequestException:
        return False
    return True


@celery.task
def sleep_task(task_details: TaskOut) -> int:
    import time
    task_details.id = sleep_task.request.id
    seconds = task_details.payload.input
    time.sleep(seconds)
    notify_task.delay(task_details)
    return seconds


@celery.task
def prime_task(task_details: TaskOut) -> bool:
    task_details.id = prime_task.request.id
    n = task_details.payload.input
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
def fibonacci_task(task_details: TaskOut) -> int:
    def fib(n: int) -> int:
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)

    task_details.id = fibonacci_task.request.id
    _n = task_details.payload.input
    result = fib(_n)
    notify_task.delay(task_details)
    return result


@app.get("/")
async def root():
    return {"task": "nask"}


@app.post("/")
async def notify(task_details: TaskOut):
    if task_details.id in database:
        database[task_details.id] = task_details
        if not task_details.status == "SUCCESS":
            return {"status": "task not finished"}
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="task not found")


@app.get("/api/tasks/", response_model=TaskList)
async def tasks_statuses():
    return {"tasks": [task for task in database.values()]}


@app.get("/api/tasks/{uuid}", response_model=TaskOut)
async def task_status(uuid: int | str | UUID = Path(..., title="task UUID")):
    if uuid in database:
        task_details = database[uuid]
        try:
            task_result = AsyncResult(task_details.id)
            task_details.status = task_result.status
            task_details.result = task_result.result
            return task_details
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail=f"error with task: {uuid}") from e
    raise HTTPException(status_code=404,
                        detail=f"task with id: {uuid} not found")


@app.post("/api/tasks/", response_model=TaskOut, status_code=201)
async def task_add(task_in: TaskIn):
    # Create task out object
    task_out = TaskOut(
        **task_in.dict()
    )

    # Check task type and add to queue
    if task_in.type == TaskType.sleep:
        sleep_task.delay(task_out)
    elif task_in.type == TaskType.prime:
        prime_task.delay(task_out)
    else:
        fibonacci_task.delay(task_out)

    # Add task to database
    database[task_out.id] = task_out

    # Return task
    return task_out
