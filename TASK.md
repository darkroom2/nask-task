docker compose (optional)
run on cluster (k8s directory with config)

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

Please prepare a containerized FastAPI-based application, independent of the platform and operating system, prepared to
run on a computing cluster, performing a long asynchronous task after sending a POST request to the endpoint
/api/tasks (there may be multiple requests to this address). The application should send the result of the task in JSON
format to the URL specified when sending the query. The ability to view the status of a task via API and queuing tasks
is welcome. Any technologies and libraries can be used.

The solution in the form of source code and its description of the approach used as well as the entire application and
instructions for running it, please send in a zipped archive in response to this email.

PL

Proszę przygotować skonteneryzowaną aplikację opartą o FastAPI (niezależną od platformy i systemu operacyjnego – mile
widziana możliwość działania na klastrze obliczeniowym) wykonującą długie asynchroniczne zadanie po przesłaniu zapytania
POST pod endpoint /api/tasks (może napływać wiele zapytań pod ten adres). Aplikacja powinna wysłać wynik zadania w
formacie JSON pod wskazany przy wysłaniu zapytania adres URL. Mile widziana możliwość podglądu statusu zadania poprzez
API oraz kolejkowania zadań. Można korzystać z dowolnych technologii i bibliotek.

Rozwiązanie w postaci kodu źródłowego oraz jego opisu zastosowanego podejścia, jak i całej aplikacji i instrukcji
uruchomienia proszę przesłać w spakowanym archiwum w odpowiedzi na tego maila.