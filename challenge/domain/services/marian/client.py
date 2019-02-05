from __future__ import division, print_function, unicode_literals

from dynaconf import settings
from websocket import create_connection


class MarianClientError(Exception):
    """Marian client error."""


class Client:
    def __init__(self):
        pass

    def request_translation(self, text):
        """Send a translation request to Marian-NMT server.

        Args:
            text (str): Input text to be translated.

        Returns:
            translated_text (str): The translated text.

        """
        ws = create_connection(settings.MARIAN_SERVER_URI)
        ws.send(text)
        translated_text = ws.recv()
        ws.close()
        return translated_text
