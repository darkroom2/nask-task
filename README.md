# nask-task

A containerized FastAPI-based application that performs several types of long asynchronous tasks.

## Description

The application provides API for adding tasks to the queue to be executed asynchronously and checking the status of the
task. After each task is completed, the result is sent to the address specified in the request.

Features:

* containerized using Dockerfile and Docker Compose
* uses FastAPI
* uses Celery task queueing with RabbitMQ as a broker and Redis as a backend
* endpoint `/api/tasks` handles multiple inquiries to this address
* task status through API

TODO:

* ready for k8s
* make diagram
* make description
* try to add k8s deployment
* Scaling
* run one uvicorn process per container (or pod) - configure replication at the cluster level, with multiple containers
  and nginx to load balance between them
* run multiple celery (autoscaling) workers per container (or pod) - configure replication at the cluster level and
  nginx to load balance between them (check if replicated uvicorn processes can share all the celery workers in all
  pods/containers)
* Write api documentation or fill OpenAPI
* run on cluster (k8s directory with config)
* kubernetes init container (for nask-task)
* write some tests

Endpoints:

* `/api/tasks`
    * `POST` - add task to the queue
    * `GET` - get all tasks
* `/api/tasks/<id>`
    * `GET` - get task status by id

Example requests:

* Hello, World!

```http request
GET http://127.0.0.1:8000/
Accept: application/json
```

```json
{
  "task": "nask"
}
```

* Add task to queue:

sleep task

```http request
POST http://127.0.0.1:8000/api/tasks
Accept: application/json
Content-Type: application/json


{
    "type": "sleep",
    "notify_url": "http://nask-task-app:8000/",
    "payload": {
        "input": 30
    }
}
```

```json
{
  "type": "sleep",
  "notify_url": "http://nask-task-app:8000/",
  "payload": {
    "input": 30
  },
  "id": "cf094e85-84ec-41b1-8fce-c7194ae51f05",
  "status": null,
  "result": null
}
```

fibonacci task

```http request
POST http://127.0.0.1:8000/api/tasks
Accept: application/json
Content-Type: application/json


{
    "type": "fibonacci",
    "notify_url": "http://nask-task-app:8000/",
    "payload": {
        "input": 30
    }
}
```

```json
{
  "type": "fibonacci",
  "notify_url": "http://nask-task-app:8000/",
  "payload": {
    "input": 30
  },
  "id": "2bf85c35-830d-405c-93b3-15ccf2eee722",
  "status": null,
  "result": null
}
```

* Get task status by id:

```http request
GET http://127.0.0.1:8000/api/tasks/522377c1-1c23-427f-b31f-30bc2eea8e33
Accept: application/json
```

```json
{
  "type": "sleep",
  "notify_url": "http://nask-task-app:8000/",
  "payload": {
    "input": 30
  },
  "id": "cf094e85-84ec-41b1-8fce-c7194ae51f05",
  "status": "PENDING",
  "result": null
}
```

* Get all tasks in queue:

```http request
GET http://127.0.0.1:8000/api/tasks
Accept: application/json
```

```json
{
  "tasks": [
    {
      "type": "sleep",
      "notify_url": "http://nask-task-app:8000/",
      "payload": {
        "input": 30
      },
      "id": "cf094e85-84ec-41b1-8fce-c7194ae51f05",
      "status": "SUCCESS",
      "result": 30
    }, {
      "type": "fibonacci",
      "notify_url": "http://nask-task-app:8000/",
      "payload": {
        "input": 30
      },
      "id": "2bf85c35-830d-405c-93b3-15ccf2eee722",
      "status": "SUCCESS",
      "result": 832040
    }
  ]
}
```

* Send notification when task is completed:

```http request
POST http://127.0.0.1:8000/
Accept: application/json
Content-Type: application/json


{
    "type": "sleep",
    "notify_url": "http://nask-task-app:8000/",
    "payload": {
        "input": 30
    },
    "id": "cf094e85-84ec-41b1-8fce-c7194ae51f05",
    "status": "SUCCESS",
    "result": 30
}
```

```json
{
  "status": "ok"
}
```

## Requirements

* `python 3.10`
* `docker`
* `docker-compose-plugin` (optional)

### Running the application with Docker Compose

This method doesn't require any local dependencies to be installed beforehand (except docker and docker-compose-plugin).

Build `nask_task_app` custom docker image:

```shell
docker-compose build
```

Download images & run all containers:

```shell
docker compose up
```

Now you can access the application at http://localhost:8000.

The docs for the API are available at http://localhost:8000/docs.

There is also flower instance available at http://localhost:5555 and RabbitMQ Management interface
at http://localhost:15672.

### Running with dependencies with Docker and application locally

#### Run Docker services

Run redis with docker:

```shell
docker run -p 6379:6379 --name nask-task-redis -d redis
```

To test if Redis is up and running, run:

```shell
docker exec -it nask-task-redis redis-cli ping
```

Run RabbitMQ with docker:

```shell
docker run -p 15672:15672 -p 5672:5672 --name nask-task-rabbit -d rabbitmq:management
```

Test if RabbitMQ is up and running, run:

```shell
docker exec -it nask-task-rabbit rabbitmqctl status
```

#### Installing local dependencies

To install dependencies for `nask_task_app` run:

```shell
pip install -r nask_task_app/requirements.txt
```

To be able to run test, also install `dev` packages:

```shell
pip install -r nask_task_app/requirements-dev.txt
```

To run celery worker run:

```shell
celery -A nask_task_app.src.main.celery worker -l info
```

To run flower (celery monitoring tool) run:

```shell
celery -A nask_task_app.src.main.celery flower
```

To run `nask_task_app` run:

```shell
uvicorn nask_task_app.src.main:app --reload --env-file .envs/.dev 
```

### Testing

To run test along with other tools (yapf, flake8, coverage) run:

```shell
./precommit.sh
```
