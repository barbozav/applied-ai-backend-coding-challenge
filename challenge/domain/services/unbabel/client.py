from urllib.parse import urljoin

import requests

SANDBOX_API_URL = 'https://sandbox.unbabel.com/tapi/v2/'


class UnbabelClientError(Exception):
    """Unbabel client error."""


class Client:
    """Unbabel's API minimal client.

    Attributes:
        _headers (dict): A JSON header with authentication for the
            API requests.

    Args:
        client (str): API client string for connection with the API.
        token (str): API token string for connection with the API.
        url (str): The Unbabel's API URL for API requests.

    """

    def __init__(self, client, token, url=SANDBOX_API_URL):
        self._url = url

        self._headers = {
            'Content-Type': 'application/json',
            'Authorization': f'ApiKey {client}:{token}'
        }

    def _get(self, url):
        try:
            response = requests.get(url, headers=self._headers)
        except:  # noqa: E722
            raise UnbabelClientError(f'Failed to GET "{url}".')
        if response.status_code > 400:
            raise UnbabelClientError(f'Failed to GET "{url}".')
        return response

    def _post(self, url, payload):
        try:
            response = requests.post(url, json=payload, headers=self._headers)
        except:  # noqa: E722
            raise UnbabelClientError(f'Failed to POST {payload} to "{url}".')
        if response.status_code > 400:
            raise UnbabelClientError(f'Failed to POST {payload} to "{url}".')
        return response

    def request_translation(self,
                            input,
                            source_language,
                            target_language,
                            callback_url=None):
        """Send a manual translation request to Unbabel's API.

        Args:
            input (str): Input text to be translated.
            source_language (str): Original (source) text language, for
                instance: 'en' for English, 'es' for Spanish, 'pt' for
                Portuguese.
            target_language (str): Translated (target) text language.
            callback_url (str): A calllback URL in which the Unbabel's
                API will post whenever the translation is finished.

        Returns:
            dict: A JSON dictionary with the API response payload.

        """
        url = urljoin(self._url, 'translation')

        payload = {
            'text': input,
            'source_language': source_language,
            'target_language': target_language,
        }

        if callback_url:
            payload['callback_url'] = callback_url

        return self._post(url, payload).json()

    def get_translation(self, id):
        """Send a manual translation request to Unbabel's API.

        Args:
            id (str): A translation ID to track the Unbabel's manual
                translation process which is returned after the request
                for a new translation.

        Returns:
            dict: A JSON dictionary with the API response payload.

        """
        url = urljoin(self._url, f'translation/{id}')
        return self._get(url).json()
