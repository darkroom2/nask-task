from enum import Enum
from os import environ, getcwd  # TODO: remove cwd
from uuid import UUID

from celery import Celery
from dotenv import load_dotenv  # TODO: remove
from fastapi import FastAPI, HTTPException
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
    id: int | str | UUID
    status: str


class TaskList(BaseModel):
    tasks: list[TaskOut]


database = {
    1: TaskOut(id=1, type=TaskType.sleep, status="waiting",
               notify_url="http://127.0.0.1:8000/",
               payload=TaskPayload(input=5)),
    2: TaskOut(id=2, type=TaskType.prime, status="running",
               notify_url="http://127.0.0.1:8000/",
               payload=TaskPayload(input=10)),
    3: TaskOut(id=3, type=TaskType.fibonacci, status="done",
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
def sleep_task(seconds):
    import time
    time.sleep(seconds)
    return seconds


@celery.task
def prime_task(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


@celery.task
def fibonacci_task(n):
    if n <= 1:
        return n
    return fibonacci_task(n - 1) + fibonacci_task(n - 2)


@app.get("/")
async def root():
    return {"task": "nask"}


@app.get("/api/tasks/", response_model=TaskList)
async def tasks_statuses():
    return {"tasks": [task for task in database.values()]}


@app.get("/api/tasks/{_id}", response_model=TaskOut | None)
async def task_status(_id: int):
    if _id in database:
        return database[_id]
    raise HTTPException(
        status_code=404,
        detail=f"Task with id: {_id} not found"
    )


@app.post("/api/tasks/", response_model=TaskOut, status_code=201)
async def task_status(task_in: TaskIn):
    # Retrieve input from payload
    _input = task_in.payload.input

    # Check task type and add to queue
    if task_in.type == TaskType.sleep:
        task = sleep_task.delay(_input)
    elif task_in.type == TaskType.prime:
        task = prime_task.delay(_input)
    else:
        task = fibonacci_task.delay(_input)

    # TODO: Add something to monitor queue position or percent done
    #  Figure out how to store the AsyncResponse returned by Celery task

    # Create task out object
    task_out = TaskOut(
        **task_in.dict(),
        id=task.id,
        status=task.status,
    )

    # Add task to database
    database[task_out.id] = task_out

    # Return task
    return task_out
