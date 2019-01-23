import time

import dramatiq

from challenge.application import repository  # noqa:F401
from challenge.application import app, projections, translator


@dramatiq.actor
def projections_task(id):
    """ Task for updating the read-model of an aggregate.

    As the read-model doesn't need to be updated in real-time, a worker
    is scheduled to do these updates when possible.

    Args:
        id (string): An aggregate UUID4 string.
    """
    projections.update(id)


@dramatiq.actor
def translation_task(id):
    """ Task for processing a translation.

    This task is responsible for requesting the translation service to
    translated a given text from English to Spanish.

    The Translation aggregate is already created and persisted, so this
    task must fetch its data. If for some reason the application goes
    down, it's possible to reprocess "requested" translations adding
    their IDs to the workers queue.

    After sending a request to the translation service, this worker will
    persist a tracking identifier and poll this translation until it's
    finished.

    Args:
        id (string): The translation aggregate UUID4 string.
    """
    translation = repository.get(id)
    translation = translator.process(translation)
    repository.save(translation)
    projections_task.send(id)
