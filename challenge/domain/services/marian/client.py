import json
from urllib.parse import urljoin

from dynaconf import settings

from challenge.domain.services.publisher import Publisher


class Client:
    def __init__(self):
        self._publisher = Publisher(settings.NMT_QUEUE)

    def request_translation(self, input, callback_url=None):
        payload = []
        payload.append(input)

        if callback_url:
            payload.append(callback_url)

        self._publisher.publish(json.dumps(payload))
