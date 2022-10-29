from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl


class TaskType(str, Enum):
    sleep = "sleep"
    prime = "prime"
    fibonacci = "fibonacci"


class TaskStatus(str, Enum):
    waiting = "waiting"
    running = "running"
    done = "done"


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
    1: TaskOut(id=1, type=TaskType.sleep, status=TaskStatus.waiting,
               percent_done=0, queue_position=42,
               notify_url="http://127.0.0.1:8000/", payload={"input": 5}),
    2: TaskOut(id=2, type=TaskType.prime, status=TaskStatus.running,
               percent_done=42, queue_position=0,
               notify_url="http://127.0.0.1:8000/", payload={"input": 10}),
    3: TaskOut(id=3, type=TaskType.fibonacci, status=TaskStatus.done,
               percent_done=100, queue_position=0,
               notify_url="http://127.0.0.1:8000/", payload={"input": 101})
}

task_queue = []

app = FastAPI()


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
    # Validate input
    print(task_in.payload)
    if not task_in.payload:
        raise HTTPException(
            status_code=422,
            detail="Payload is empty"
        )

    _id = len(database) + 1

    # Add task to queue
    task_out = TaskOut(
        **task_in.dict(),
        id=_id,
        status=TaskStatus.waiting,
        percent_done=0,
        queue_position=len(task_queue),
    )
    task_queue.append(task_out)

    # Add task to database
    database[_id] = task_out

    # TODO: Add something to monitor queue position or percent done

    return database[_id]
