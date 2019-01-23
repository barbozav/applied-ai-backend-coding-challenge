import sys

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dynaconf import FlaskDynaconf, settings
from flask import Flask
from flask_bootstrap import Bootstrap

from challenge.domain.model.translation import Translation
from challenge.domain.services.translator import Translator
from challenge.domain.projections import TranslationProjections
from challenge.domain.repositories import AggregatesRepository
from challenge.persistence import create_db, create_tables
from challenge.persistence.eventstore import model as e_model  # noqa: F401
from challenge.persistence.eventstore.postgresql import PostgresEventStore
from challenge.persistence.projections import model as p_model  # noqa: F401
from challenge.persistence.projections.postgresql import PostgresTranslation
from challenge.utils.logging import logger

# Workaround an un-configured environment
if (not settings.get('API_CLIENT')) or (not settings.get('API_TOKEN')) or (
        not settings.get('API_CALLBACK')):
    logger.error(f'Have you configured the ".env" file?')
    while True:
        pass


def setup_database():
    """Set up database and create tables.

    For this application purpose, the database is running alongside with
    the application containers and a new schema is created at every
    startup.

    In production, a hosted database should be used and creating the
    whole schema and all tables would be unnecessary.

    """
    logger.info('creating databases')
    db = create_db()
    # Comment the line below if not using a container'ized database.
    create_tables(db)
    return db


def create_repository():
    """Create repository.

    It works as an interface between application and persisted data for
    the event sourcing design (write-model).

    Other repositories could be set here.

    """
    logger.info('creating event sourced repositories')
    return AggregatesRepository(Translation, PostgresEventStore())


def create_projections():
    """Create repository.

    It works as an interface between application and persisted data for
    visualization with relevant information for queries (read-model).

    Other projections could be set here.

    """
    logger.info('creating read model projections')
    return TranslationProjections(PostgresTranslation())


def setup_worker():
    """Set up Dramatiq with Redis as a queue.

    Dramatiq manages the message passing to background workers which run
    long tasks to avoid stalling the application responses for too long.

    Redis is used as a message queue for simplicity sake. A more robust
    infrastructure could configure a RabbitMQ here, for example.

    """
    logger.info('creating tasks queue')
    broker = RedisBroker(url=f'{settings.REDIS_URL}')
    dramatiq.set_broker(broker)


def create_app():
    """Create Flask application and initialize Flask extensions.

    This application reads configuration from environment variables
    using FlaskDynaconf extension.
    It uses the Bootstrap extension for the frontend and also for the
    frontend (dynamic updates), an event server is set with the
    Flask-SSE blueprint.

    """
    logger.info('starting application')
    app = Flask(__name__)
    Bootstrap(app)
    FlaskDynaconf(app)

    return app


db = setup_database()
repository = create_repository()
projections = create_projections()
translator = Translator(settings.API_SOURCE_LANGUAGE,
                        settings.API_TARGET_LANGUAGE)
setup_worker()
app = create_app()

from challenge.application import routes  # noqa: F401
