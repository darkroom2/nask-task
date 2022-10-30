# nask-task

A containerized FastAPI-based application that performs several types of long asynchronous tasks.

## Description

The application provides API for adding tasks to the queue to be executed asynchronously and checking the status of the
task. After each task is completed, the result is sent to the address specified in the request.

Features:

* Containerized app
* uses FastAPI
* ready for k8s
* uses Celery (task queue, long async tasks, returns results to the address specified in the request)
* endpoint `/api/tasks` handles multiple inquiries to this address
* Task status through API

TODO:

* remove code TODOs
* remove dotenv()
* update README.md with proper requests and responses
* write celery tests
* make diagram
* make description
* try to add k8s deployment
* add pylint, coverage, flake8 or autopep8 (and instructions)

Endpoints:

* `/api/tasks`
  * `POST` - add task to the queue
  * `GET` - get all tasks
* `/api/tasks/<id>`
  * `GET` - get task status by id

Example requests:

* Get all tasks in queue:

```http request
GET http://127.0.0.1:8000/api/tasks
Accept: application/json
```

```json
{
  "tasks": [
    {
      "id": 1,
      "type": "sleep",
      "status": "PENDING",
      "notify_url": "http://127.0.0.1:8000/",
      "payload": {
        "input": 5
      }
    },
    {
      "id": 2,
      "type": "prime",
      "status": "STARTED",
      "notify_url": "http://127.0.0.1:8000/",
      "payload": {
        "input": 10
      }
    },
    {
      "id": 3,
      "type": "fibonacci",
      "status": "SUCCESS",
      "notify_url": "http://127.0.0.1:8000/",
      "payload": {
        "input": 101
      }
    }
  ]
}
```

* Get task status by id:

```http request
GET http://127.0.0.1:8000/api/tasks/1
Accept: application/json
```

```json
{
  "id": 1,
  "type": "sleep",
  "status": "STARTED",
  "notify_url": "http://127.0.0.1:8000/",
  "payload": {
    "input": 5
  }
}
```

* Add task to queue:

```http request
POST http://127.0.0.1:8000/api/tasks
Accept: application/json
Content-Type: application/json

{
  "type": "prime",
  "notify_url": "http://127.0.0.1:8000/",
  "payload": {
    "input": 100
  }
}
```

```json
{
  "id": 4,
  "type": "prime",
  "status": "PENDING",
  "notify_url": "http://127.0.0.1:8000/",
  "payload": {
    "input": 100
  }
}
```

## Requirements

* python 3.10
* docker
* docker-compose-plugin (optional)

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

```bash
docker run -p 6379:6379 --name nask-task-redis -d redis
```

To test if Redis is up and running, run:

```bash
docker exec -it nask-task-redis redis-cli ping
```

Run RabbitMQ with docker:

```bash
docker run -p 15672:15672 -p 5672:5672 --name nask-task-rabbit -d rabbitmq:management
```

Test if RabbitMQ is up and running, run:

```bash
docker exec -it nask-task-rabbit rabbitmqctl status
```

#### Installing local dependencies

To install dependencies for `nask_task_app` run:

```bash
pip install -r nask_task_app/requirements.txt
```

To be able to run test, also install `dev` packages:

```shell
pip install -r nask_task_app/requirements-dev.txt
```

To run celery worker run:

```shell
celery -A nask_task_app.app.main.celery worker -l info
```

To run flower (celery monitoring tool) run:

```shell
celery -A nask_task_app.app.main.celery flower
```

To run `nask_task_app` run:

```shell
uvicorn nask_task_app.app.main:app --reload --env-file .envs/.dev 
```

TODO:

Scaling:

* run one uvicorn process per container (or pod) - configure replication at the cluster level, with multiple containers
  and nginx to load balance between them
* run multiple celery (autoscaling) workers per container (or pod) - configure replication at the cluster level and
  nginx to load balance between them (check if replicated uvicorn processes can share all the celery workers in all
  pods/containers)

* Write api documentation or fill OpenAPI
* run on cluster (k8s directory with config)
* kubernetes init container (for nask-task)
* use celery + redis
* write some tests

[]: # ## Kubernetes
[]: # ### Deploy
[]: # ```bash
[]: # kubectl apply -f k8s
[]: # ```
[]: # ### Undeploy
[]: # ```bash
[]: # kubectl delete -f k8s
[]: # ```
