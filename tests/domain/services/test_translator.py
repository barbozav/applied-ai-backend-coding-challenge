from unittest.mock import patch

from challenge.domain.model.translation import Translation
from challenge.domain.services.translator import Translator
from tests.fixtures import constants


class TestTranslator():
    def test_process_return_pending_translation(self):
        translation = Translation.create(constants.API_PAYLOAD['text'])
        service = Translator(constants.API_PAYLOAD['source_language'],
                             constants.API_PAYLOAD['target_language'])

        translation = service.process(translation)

        assert isinstance(translation, Translation)
        assert translation.status == 'pending'

    @patch(
        'challenge.domain.services.unbabel.client.Client.request_translation')
    def test_process_requests_translation_once(self, request_translation):
        translation = Translation.create(constants.API_PAYLOAD['text'])
        service = Translator(constants.API_PAYLOAD['source_language'],
                             constants.API_PAYLOAD['target_language'])

        translation = service.process(translation)

        assert request_translation.call_count == 1

    def test_process_invalid_return_aborted_translation(self):
        translation = Translation.create(constants.API_PAYLOAD['text'])
        service = Translator(constants.API_PAYLOAD_INVALID_LANGUAGE,
                             constants.API_PAYLOAD_INVALID_LANGUAGE)

        translation = service.process(translation)

        assert isinstance(translation, Translation)
        assert translation.status == 'aborted'
