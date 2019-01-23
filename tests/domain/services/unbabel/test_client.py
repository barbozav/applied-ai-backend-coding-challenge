import json

import pytest

from challenge.domain.services.unbabel.client import Client, UnbabelClientError
from tests.fixtures import constants


class TestClient():
    def test_request_translation_payload(self):
        c = Client(constants.API_CLIENT, constants.API_TOKEN,
                   constants.API_URL)
        r = c.request_translation(
            constants.API_PAYLOAD['text'],
            constants.API_PAYLOAD['source_language'],
            constants.API_PAYLOAD['target_language'],
            callback_url=constants.API_CALLBACK)

        assert 'callback_url' in r.keys()
        assert 'order_number' in r.keys()
        assert 'price' in r.keys()
        assert 'source_language' in r.keys()
        assert 'status' in r.keys()
        assert 'target_language' in r.keys()
        assert 'text' in r.keys()
        assert 'text_format' in r.keys()
        assert 'uid' in r.keys()

        assert r['callback_url'] == constants.API_CALLBACK
        assert r['price'] == constants.API_PAYLOAD['price']
        assert r['source_language'] == constants.API_PAYLOAD['source_language']
        assert r['status'] == constants.API_PAYLOAD_STATUS_NEW
        assert r['target_language'] == constants.API_PAYLOAD['target_language']
        assert r['text'] == constants.API_PAYLOAD['text']
        assert r['text_format'] == constants.API_PAYLOAD['text_format']

    def test_get_translation_payload(self):
        c = Client(constants.API_CLIENT, constants.API_TOKEN)
        r = c.get_translation(constants.API_PAYLOAD['uid'])

        assert 'order_number' in r.keys()
        assert 'price' in r.keys()
        assert 'source_language' in r.keys()
        assert 'status' in r.keys()
        assert 'target_language' in r.keys()
        assert 'text' in r.keys()
        assert 'text_format' in r.keys()
        assert 'translatedText' in r.keys()
        assert 'uid' in r.keys()

        assert r == constants.API_PAYLOAD

    def test_request_invalid_client_raises_client_error(self):
        c = Client(constants.API_INVALID_CLIENT, constants.API_TOKEN)
        with pytest.raises(UnbabelClientError):
            c.request_translation(
                constants.API_PAYLOAD['text'],
                constants.API_PAYLOAD['source_language'],
                constants.API_PAYLOAD['target_language'],
                callback_url=constants.API_CALLBACK)

    def test_request_invalid_token_raises_client_error(self):
        c = Client(constants.API_CLIENT, constants.API_INVALID_TOKEN)
        with pytest.raises(UnbabelClientError):
            c.request_translation(
                constants.API_PAYLOAD['text'],
                constants.API_PAYLOAD['source_language'],
                constants.API_PAYLOAD['target_language'],
                callback_url=constants.API_CALLBACK)

    def test_request_invalid_url_raises_client_error(self):
        c = Client(constants.API_CLIENT, constants.API_TOKEN,
                   constants.API_INVALID_URL)
        with pytest.raises(UnbabelClientError):
            c.request_translation(
                constants.API_PAYLOAD['text'],
                constants.API_PAYLOAD['source_language'],
                constants.API_PAYLOAD['target_language'],
                callback_url=constants.API_CALLBACK)

    def test_request_invalid_source_language_raises_client_error(self):
        c = Client(constants.API_CLIENT, constants.API_TOKEN,
                   constants.API_INVALID_URL)
        with pytest.raises(UnbabelClientError):
            c.request_translation(
                constants.API_PAYLOAD['text'],
                constants.API_PAYLOAD_INVALID_LANGUAGE,
                constants.API_PAYLOAD['target_language'],
                callback_url=constants.API_CALLBACK)

    def test_request_invalid_target_language_raises_client_error(self):
        c = Client(constants.API_CLIENT, constants.API_TOKEN,
                   constants.API_INVALID_URL)
        with pytest.raises(UnbabelClientError):
            c.request_translation(
                constants.API_PAYLOAD['text'],
                constants.API_PAYLOAD['source_language'],
                constants.API_PAYLOAD_INVALID_LANGUAGE,
                callback_url=constants.API_CALLBACK)
