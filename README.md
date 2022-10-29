# nask-task

A containerized FastAPI-based application that performs several types of long asynchronous tasks.

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

docker compose (celery autoscaling)
run on cluster (k8s directory with config)
poetry to resolve dependencies
kubernetes init container (for nask-task)

use celery + redis
write some tests

task = {task_id, task_type, task_status, task_precent_done}

post request /api/tasks:(result_url, task_type, task_input) > if valid:({task}, queue_position) else:400
get request /api/tasks:() > list({task_id, task_type, precent_done}, ..., {...})
get request /api/tasks/<task_id> ({task})

[]: # # Usage
[]: # ## Docker
[]: # ### Build
[]: # ```bash
[]: # docker build -t nask-task .
[]: # ```
[]: # ### Run
[]: # ```bash
[]: # docker run -p 8000:8000 nask-task
[]: # ```
[]: # ## Kubernetes
[]: # ### Deploy
[]: # ```bash
[]: # kubectl apply -f k8s
[]: # ```
[]: # ### Undeploy
[]: # ```bash
[]: # kubectl delete -f k8s
[]: # ```
[]: # ## Usage
[]: # ### Post request
[]: # ```bash
[]: # curl -X POST http://localhost:8000/task -d '{"result_url": "http://localhost:8000/result", "task_type": "fibonacci"}'
[]: # ```
[]: # ### Get request
[]: # ```bash
[]: # curl -X GET http://localhost:8000/result
[]: # ```
[]: # ## Task types
[]: # ### Fibonacci
[]: # ```bash
[]: # curl -X POST http://localhost:8000/task -d '{"result_url": "http://localhost:8000/result", "task_type": "fibonacci"}'
[]: # ```
[]: # ### Prime numbers
[]: # ```bash
[]: # curl -X POST http://localhost:8000/task -d '{"result_url": "http://localhost:8000/result", "task_type": "prime_numbers"}'
[]: # ```
[]: # ### Sleep
[]: # ```bash
[]: # curl -X POST http://localhost:8000/task -d '{"result_url": "http://localhost:8000/result", "task_type": "sleep"}'
[]: # ```
[]: # ## Result
[]: # ```bash
[]: # curl -X GET http://localhost:8000/result
[]: # ```
[]: # ## Result example
[]: # ```json
[]: # {
[]: #   "result": "fibonacci",
[]: #   "status": "done"
[]: # }
[]: # ```
[]: # ## Result status
[]: # ### Done
[]: # ```json
[]: