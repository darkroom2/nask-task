from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl


class TaskType(str, Enum):
    task1 = 'task1'
    task2 = 'task2'
    task3 = 'task3'


class TaskStatus(str, Enum):
    waiting = 'waiting'
    running = 'running'
    done = 'done'


class TaskOut(BaseModel):
    id: int
    type: TaskType
    status: TaskStatus
    percent_done: int
    queue_position: int
    notify_url: HttpUrl
    payload: dict


class TaskIn(BaseModel):
    type: TaskType
    notify_url: HttpUrl
    payload: dict


class TaskList(BaseModel):
    tasks: list[TaskOut]


database = {
    1: TaskOut(id=1, type=TaskType.task1, status=TaskStatus.waiting,
               percent_done=0, queue_position=42,
               notify_url='http://127.0.0.1:8000/', payload={'foo': 'bar'}),
    2: TaskOut(id=2, type=TaskType.task2, status=TaskStatus.running,
               percent_done=42, queue_position=0,
               notify_url='http://127.0.0.1:8000/', payload={'bar': 'baz'}),
    3: TaskOut(id=3, type=TaskType.task3, status=TaskStatus.done,
               percent_done=100, queue_position=0,
               notify_url='http://127.0.0.1:8000/', payload={'baz': 'foo'})
}

queue_length = 0

app = FastAPI()


@app.get("/")
async def root():
    return {"task": "nask"}


@app.get("/api/tasks/", response_model=TaskList)
async def tasks_statuses():
    return {'tasks': [task for task in database.values()]}


@app.get("/api/tasks/{_id}", response_model=TaskOut | None)
async def task_status(_id: int):
    if _id in database:
        return database[_id]


@app.post("/api/tasks/", response_model=TaskOut)
async def task_status(task_in: TaskIn):
    # Validate input
    # Add task to queue
    # Return task status
    # Add something to monitor queue position or percent done

    _id = len(database) + 1
    task_out = TaskOut(
        **task_in.dict(),
        id=_id,
        status=TaskStatus.waiting,
        percent_done=0,
        queue_position=queue_length + 1
    )

    database[_id] = task_out  # Adding to db might raise an error
    return database[_id]  # Read from db to assure that task was added
