import json
from urllib.parse import urljoin

from dynaconf import settings

from challenge.domain.services.publisher import Publisher


class MarianClientError(Exception):
    """Marian client error."""


class Client:
    def __init__(self):
        self._publisher = Publisher(settings.NMT_QUEUE)

    def request_translation(self,
                            input,
                            source_language,
                            target_language,
                            callback_url=None):
        """Send a translation request to a Marian-NMT worker.

        Args:
            input (str): Input text to be translated.
            source_language (str): Original (source) text language, for
                instance: 'en' for English, 'es' for Spanish, 'pt' for
                Portuguese.
            target_language (str): Translated (target) text language.
            callback_url (str): A calllback URL in which the Marian-NMT
                worker will post whenever the translation is finished.

        """
        payload = {
            'text': input,
            'source_language': source_language,
            'target_language': target_language,
        }

        if callback_url:
            payload['callback_url'] = callback_url

        try:
            self._publisher.publish(json.dumps(payload))
        except:  # noqa: E722
            raise MarianClientError(f'Failed to schedule task.')
