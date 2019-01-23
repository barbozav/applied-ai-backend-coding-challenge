from urllib.parse import urljoin

from dynaconf import settings

from challenge.domain.model.translation import (
    TranslationAborted, TranslationFinished, TranslationPending)
from challenge.domain.services.unbabel.client import Client
from challenge.utils.logging import logger

_translation_pending = ['new', 'accepted', 'translating']
_translation_finished = ['rejected', 'canceled', 'failed', 'completed']


class Translator:
    """Responsible for processing requested translations.

    It calls translation services - which could be internal or external
    (and in our case it is an external service through the Unbabel's
    API) and parse its response to fit the Translation model in our
    application domain.

    If a translation service is to be changed, it is changed in here.

    Args:
        source_language (str): Original (source) text language, for
                instance: 'en' for English, 'es' for Spanish, 'pt' for
                Portuguese.
            target_language (str): Translated (target) text language.

    """

    def __init__(self, source_language, target_language):
        self._client = Client(
            client=settings.API_CLIENT,
            token=settings.API_TOKEN,
            url=settings.API_URL)

        self._source_language = source_language
        self._target_language = target_language

    def process(self, translation):
        """Process a requested translation and update its status.

        As its through an external service, it changes the Translation
        resource status to "pending" after snding a request to the
        Unbabel's API.

        Args:
            translation (Translation): The translation to be processed.

        """
        text = translation.text
        callback_url = urljoin(settings.API_CALLBACK, translation.id)

        logger.debug(
            f"Requesting translation with callback to '{callback_url}'")

        response = self._client.request_translation(
            text, self._source_language, self._target_language, callback_url)

        # Check for request errors
        if 'error' in response.keys():
            event = TranslationAborted.create(
                f"Request error: {response['error']}")
            translation.apply(event)

            logger.debug(f"Client returned an error: {response['error']}")

            return translation

        uid = response['uid']
        status = response['status']

        logger.debug(f'Updating translation {translation.id}:{uid}')

        if status in _translation_pending:
            event = TranslationPending.create(uid)
            translation.apply(event)
        else:
            event = TranslationAborted.create(f'Translation error: {status}')
            translation.apply(event)

        return translation

    def get(self, translation):
        """Get a requested translation (and update it if required).

        If the request resource status is different from the local
        Translation's, the local translation resource is updated
        accordingly.

        Args:
            translation (Translation): The translation to be get (and
                updated).

        """
        logger.debug(f'Requesting translation {translation.id}:'
                     f'{translation.translation_id}')
        response = self._client.get_translation(translation.translation_id)

        # Check for a response
        if response:
            uid = response['uid']
            status = response['status']

            # Check if status changed
            if (translation.status == status):
                return translation

            logger.debug(f'Updating translation {translation.id}:'
                         f'{translation.translation_id}')

            # Check wheter update a finished translation
            if status in _translation_finished:
                event = TranslationFinished.create(response['translatedText'])
                translation.apply(event)
            # Check wheter update a pending translation
            elif status in _translation_pending:
                event = TranslationPending.create(uid)
                translation.apply(event)
            # Check any other status unknown
            else:
                event = TranslationAborted.create(
                    f'Translation error: {status}')
                translation.apply(event)

        else:
            # Missing response
            logger.debug(f"Client returned an error: not found")
            event = TranslationAborted.create(f'Translation not found.')
            translation.apply(event)

        return translation
