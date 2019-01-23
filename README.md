# Unbabel Backend Challenge

Hello again, Unbabel recruiting team!

This is my solution to the [Unbabel Applied AI Challenge](https://github.com/Unbabel/applied-ai-backend-coding-challenge), based on [my previous solution](https://github.com/barbozav/backend-coding-challenge) to the Unbabel Backend Challenge.

Prevously, I've developed a Flask web application which translates (manually) input text from English to Spanish using Unbabel's API, presenting it in a list of translations dynamically updated with 3 different statuses: _requested_, _pending_ and _translated_. Tests were implemented for the domain layer - covering the translation services, event-sourcing model and repositories.

As I've chosen a domain-driven architecture, this solution integrates the Marian-decoder as a new translation service (MT) without too much changes from the rest of the source code (except for a few improvements).

Documentation consists on this README.md and source code documentation (_docstrings_). Text from the original documentation will be _italic_.

## Requirements

* *[Docker](https://www.docker.com/)*
* *[docker-compose](https://docs.docker.com/compose/)*
* *[ngrok](https://ngrok.com/) (optional for HTTP tunneling and receiving callbacks)*

## TL;DR

* *Start `ngrok`on HTTP port 5000:*

  ```bash
  ./ngrok http 5000
  ```

* *Copy the `.env.template` to a `.env` file and set the required environment variables.*

* *Run the application:*

```bash
docker-compose up -f docker-compose.yml --build --force-recreate
```

* *Access it:*

  *http://localhost:5000/*

## Roadmap and references

Here I try to break the steps I took to develop the solution - which is described later in this document.

My references are linked here alongside with the roadmap topics - some I've already implemented for other projects and some I've had to study for this challenge.

1. Fork the project. **[OK]**
2. Re-use [Unbabel Backend Challenge](https://github.com/barbozav/backend-coding-challenge) source code. **[OK]**
3. Update the README file (Introduction and Roadmap). **[OK]**
4. Study the [Marian-decoder](https://marian-nmt.github.io/).
5. Impement a simple application with the Marian-decoder.
6. Study RabbitMQ library for C++.
7. Implement a simple RabbitMQ consumer in C++.
8. Implement the Marian-decoder consumer and task.
9. Configure a Makefile.
10. Configure RabbitMQ and re-configure Dramatiq.
11. Implement a RabbitMQ producer in the worker.
12. Update the docker-compose.
13. Implement the MT service.
14. Test the MT service.
15. Update the `Translator` class to support the MT service.
16. Test the `Translator` class.
17. Improve the frontend.
18. Write _docstrings_.
19. Generate HTML documentation with [Sphinx](http://www.sphinx-doc.org/en/master/) and [doxygen](http://www.doxygen.nl/).
20. Update the a README (Sequence diagrams and documentation).
21. Organize commits with `git rebase` and clean feature branches.
22. Deliver it.

## Solution design

*I've designed the application in a simple domain-driven approach trying to keep the Flask application (application layer), the translations logic (domain layer) and the data operations (persistence layer) isolated. The following diagram summarizes the architecture described in the next sessions.*

![Domain-drive architecture layers.](./resources/architecture.png)

### Application layer

*My Flask reference is [Miguel Grinberg's Flask Mega-Tutorial book](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) which I have initially followed but as it uses available Flask extensions for everything, it makes too difficult to decouple the application layers.*

*For settings management I am using `dynaconf` and its Flask extension. For the background tasks, I let `Dramatiq` handle the queues using `Redis` cache just because it's simple to configure - but I could have used RabbitMQ as well.*

*For the frontend, I am using `Flask-Bootstrap` styles, `Flask-WTF` forms and AJAX to poll the translations list.*

*An attempt of using `Flask-SSE` to notify all clients with changes instead of AJAX polling failed - it couldn't connect to the same `Redis` cache as `Dramatiq`. Configuring 2 `Redis` instances with `docker-compose` was taking me too much time, an alternative would be using RabbitMQ for the tasks and Redis for the frontend cache instead.*

### Domain layer

*For the translation services, I've chosen an event-sourcing approach (based on [this series of blog posts](https://breadcrumbscollector.tech/implementing-event-sourcing-in-python-part-1-aggregates/)) to properly handle the translation service status changes. My interpretation of the problem suggests the following logic:*

* ***requested:** As soon as an input text is submitted to our application via the HTML forms, it is considered a requested translation.*
* ***pending:** After sent to a translation service (in our case it's Unbabel API), its status changes from requested to pending and we have to wait until its completion (as we are requesting manual translations).*
* ***finished:** When the translation service completes processing the input text (translating it from English to Spanish) and sends a POST to a callback URL in the application, our translation status changes to finished.*

*All status changes are recorded as events in an event aggregate (which is a `Translation` object). This way, instead of having only the final state of an object, we can track down every modification (e.g. timestamps) and add other events to the logic in the future (other translation services appending to the events stream - internal x external services, automatic x manual services, etc).*

*To query and visualize this information, though, I've implemented a simple read-model of the event-sourced aggregate containing the current state of every translation and required information as the string length for ordering the translations list.*

### Persistence layer

*The persistence layer is implemented with `SQLAlchemy` and a PostgreSQL database.*

> ***Note:** _Currently, we have a PostgreSQL container running within the same `docker-compose` the application runs. This is definetely not the best approach - the schema and tables are recreated everytime (or persisted in an external volume).*
>
> *This setup could be easily changed in the `.env` file assigning to a proper hosted PostgreSQL database to the database URI environment variable instead.*

*The write-model for event-sourcing is implemented with 2 tables. One for **Aggregates** and another for **Events**. The read-model for visualization (which can be generated from the write-model on demand) is a single **Translations** table. Other projections could be added (e.g. read-models for management, auditing or analytics).*

*The following schema represents the implemented challenge schema.*

![Domain-drive architecture layers.](./resources/schema.png)

> ***Note:** The `Version` column in the Aggregates table is used as an optimistic lock - if 2 transactions attempt to update the same resource, the first one will complete and increment this value. Then, the second will try to update a version that doesn't exist anymore and fail. It's a simple mechanism of robustness*

## Application steps

*The following sequence diagram is a simple "good path"-only diagram illustrating the most important components calls and behaviors. It doesn't cover all paths (e.g. ignoring error handling) and it doesn't include the read-model (projections) when updating clients. Although, it's a good "mind map" of what is happening when a new translation is requested in a browser and sent to our application.*

![Applicaton sequence diagram.](./resources/sequence.svg)

## Project organization

### Revision control

*This project follows a [Karma git](https://karma-runner.github.io/3.0/dev/git-commit-msg.html)-sh style for commit messages.*

*The single production, staging and development branches is avoided and feature branches were used instead.*

*As soon as feature branches are merged into master, they were removed. Unfortunately, no PRs and code reviews were opened during development. (As I was developing all by myself, I've forgotten how useful it could be.)*

*"Baby steps" commits are recommended, but unfortunately (Shame on me!) a bunch of them are huge and contain too much changes to be reviewed in a single pass. Usually, it gets better after a large project is already up and running.*

> ***Note:** I'll try to re-organize commits with `git rebase ` and improve the challenge reviewers experience.*

### Source Code

*The root directory contains all configuration files required:*

* *`.gitignore `and `.dockerignore`;*
* *`requirements.txt` with required Python packages;*
* *`.env.template` with environment variables which must be set before running;*
* *`docker-compose.yml` files  and `Dockerfile` for building and deploying the application;*
* *`docker-compose.tests.yml` and `Dockerfile` files for building and testing the application.*

*And documentation:*

* *This `README.md` file and its `resources`.*

*The application is developed as a `challenge` package and, as described above, it isolates the web application from the application domain and data persistence layers. The following image illustrates it with more details.*

![Application structure](./resources/structure.png)

*For development, I've used `virtuallenvwrapper` and Visual Studio Code. All Python files were linted with `Flake8` (which is faster), `pylint` (which covers more issues), `pydocstrings`, formatted with `yapf` and `isort`.*

### Tests

*As time ran short and I still need to learn how to properly test a web application from end-to-end, I've decided to test the core of this project, focusing on the happy path. There are no tests implemented for the application layer or persistence layer, but the essential classes of the domain layer were tested:*

* *The Unbabel's API client;*
* *The Translator service;*
* *The event-sourcing model (Aggregates, Events and Translations);*
* *The event-source aggregates Repository class.*

*Not all tests are isolated unit tests - this way testing the repository also stresses PostgreSQL queries from the Persistence layer, for instance. Most of these tests were implemented with `Hypothesis` Python package, which does a good job automatically generating tests cases (and corner cases).*

*The frontend tests are excluded as the application routes, templates and read-model. Studying `Selenium` could apply here.*

*A simple browser debugger or extension is capable of returning the average load time of the application `/index`page - which is around 150 ms. A better approach would be test it with `Locust` or `JMeter` and do a proper analysis - scaling worker processes and threads as necessary.*

### Build, tests and deploy

*There are `docker-compose` files for running both the application and tests with their dependencies (Redis and PostgreSQL). To do so, follow these steps:*

1. *Start an HTTP tunnel to the local port 5000 - the Unbabel's API will need a callback URL. I'm using [ngrok](https://ngrok.com/), but there are other solutions available.*

```bash
./ngrok http 5000
```

2. *Edit the `.env.template` file with the required environment variables (see the following snippet). Save it as `.env`.*

```bash
###############################################################################
# CONFIGURE THE FOLLOWING ENVIRONMENT VARIABLES BEFORE RUNNING!
###############################################################################

# API client
UNBABEL_API_CLIENT=

# API token
UNBABEL_API_TOKEN=

# API callback URL. Please, consider the following:
#    - The format MUST be 'http[s]://<host>/callback/' (with quotes).
#    - The host might be a Ngrok HTTP tunnel to your local port 5000.
#    - The endpoint MUST be "callback" as it's implemented this way.
#    - The last slash ("/") MUST be explicit
UNBABEL_API_CALLBACK=

###############################################################################
# DO NOT EDIT ANYTHING FROM NOW ON
###############################################################################

...

```

3. *Run tests.*

```bash
docker-compose up -f docker-compose.tests.yml --build --force-recreate
```

*After finishing, you will need to stop the docker-container by yourself (`CTRL + C` will do).*

```bash
challenge_app | =================== test session starts ====================
challenge_app | platform linux -- Python 3.6.7, pytest-4.1.0, py-1.7.0, pluggy-0.8.0
challenge_app | hypothesis profile 'default' -> database=DirectoryBasedExampleDatabase('/src/.hypothesis/examples')
challenge_app | rootdir: /src, inifile:
challenge_app | plugins: hypothesis-3.86.5
challenge_app | collected 28 items
challenge_app | 
challenge_app | tests/domain/test_repositories.py ..                                     [  7%]
challenge_app | tests/domain/model/test_base.py .....                                    [ 25%]
challenge_app | tests/domain/model/test_translation.py ...........                       [ 64%]
challenge_app | tests/domain/services/test_translator.py ...                             [ 75%]
challenge_app | tests/domain/services/unbabel/test_client.py .......                     [100%]
challenge_app | 
challenge_app | ===================== warnings summary =====================

...

challenge_app | ========= 28 passed, 4 warnings in 111.67 seconds ==========
challenge_app exited with code 0

```

4. *Run the application.*

```bash
docker-compose up -f docker-compose.yml --build --force-recreate
```

5. *Access the application using the HTTP tunnel or http://localhost:5000/*

![Unbabel Backend Coding Challenge](./resources/screenshot.png)

## Known Issues (or Next Steps)

*The following issues are known and yet to be fixed:*

* *`Redis` is used as a message queue for the background workers without too much configuration. It's not reliable even though `Dramatiq` is managing it. A better solution would required properly configuring a message queue system as `RabbitMQ` and adding it to the `docker-compose` files.*
* *After some time, the AJAX polling loses connection with the PostgreSQL database. It requires further investigation, but implementing the event server with `Flash-SSE` could do.*
* *After the translations list is dynamically updated, the "Newer translations" and "Older translations" buttons are not. It's required to refresh the page after 10 entries to do so.*
* *Escape characters are returned from the PostgreSQL, sent to the translation services and printed in the frontend as well. Some translators deal with it, others don't.*
* *There are no control over requests (to the databases or APIs). `Tenacity` could be of help.*
* *There are insufficient tests for the application and persistence layer.*
* *There are no stress tests to say the application is scalable.*