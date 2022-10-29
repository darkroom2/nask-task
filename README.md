# nask-task

A containerized FastAPI-based application that performs several types of long asynchronous tasks.


### Dependencies

Run redis with docker:
```bash
docker run -p 6379:6379 --name nask-task-redis -d redis
```

To test if Redis is up and running, run:
```bash
docker exec -it nask-task-redis redis-cli ping
```

### Application

To install nask-task run:
```bash
pip install -r requirements.txt
```

To run nask-task run:
```bash
uvicorn main:app --reload
```
