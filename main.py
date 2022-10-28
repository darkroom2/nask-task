from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"task": "nask"}


"""
GET returns state of a tasks (% done of current task) and queue size
"""


@app.get("/api/tasks/")
async def tasks_status(_id: int):
    if _id == 1:
        return {"id": _id, "type": "", "status": "done", "queue": 0}
    return {"id": _id, "status": "in-progress", "queue": 1}


""" 
POST creates a new task and returns task id
"""


@app.post("/api/tasks/")
async def create_task(name: str):
    return {"message": f"Hello {name}"}
