from datetime import datetime
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from hypothesis import given

from challenge.domain.model.base import Aggregate, Event
from challenge.domain.model.errors import InvalidEventError, InvalidStatusError
from challenge.domain.model.translation import (
    Translation, TranslationFinished, TranslationPending, TranslationRequested)
from tests.fixtures import constants
from tests.fixtures.strategies import (invalid_translation_changes, valid_id,
                                       valid_text, valid_translation_changes)


class TestTranslationRequested:
    def test_create_returns_event(self):
        event = TranslationRequested.create('')
        assert isinstance(event, Event)
        assert isinstance(event, TranslationRequested)

    @given(text=valid_text())
    def test_create_sets_text(self, text):
        event = TranslationRequested.create(text)
        assert event.text == text


class TestTranslationPending:
    def test_create_returns_event(self):
        event = TranslationPending.create('')
        assert isinstance(event, Event)
        assert isinstance(event, TranslationPending)

    @given(translation_id=valid_id())
    def test_create_sets_translation_id(self, translation_id):
        event = TranslationPending.create(translation_id)
        assert event.translation_id == translation_id


class TestTranslationFinished:
    def test_create_returns_event(self):
        event = TranslationFinished.create('')
        assert isinstance(event, Event)
        assert isinstance(event, TranslationFinished)

    @given(translated_text=valid_text())
    def test_create_sets_translated_text(self, translated_text):
        event = TranslationFinished.create(translated_text)
        assert event.translated_text == translated_text


class TestTranslation:
    def test_create_returns_aggregate(self):
        translation = Translation.create('')
        assert isinstance(translation, Aggregate)
        assert isinstance(translation, Translation)

    @given(text=valid_text())
    def test_create_applies_requested_event(self, text):
        translation = Translation.create(text)
        with freeze_time(constants.NOW):
            with patch('uuid.uuid4', return_value=constants.UUID4):
                translation = Translation.create(text)
                requested = TranslationRequested.create(text)

        assert translation.changes == [requested]
        assert translation.text == requested.text
        assert translation.finished is False

    @given(changes=valid_translation_changes())
    def test_apply_appends_events(self, changes):

        requested = changes[0]
        now = requested.occurred_at
        text = requested.text
        uuid4 = requested.id

        with freeze_time(now):
            with patch('uuid.uuid4', return_value=uuid4):
                translation = Translation.create(text)

            for event in changes:
                if isinstance(event, TranslationRequested):
                    continue
                translation.apply(event)

        assert translation.changes == changes

    @given(changes=valid_translation_changes())
    def test_apply_triggers_events(self, changes):
        requested = changes[0]
        now = requested.occurred_at
        text = requested.text
        uuid4 = requested.id

        with freeze_time(now):
            with patch('uuid.uuid4', return_value=uuid4):
                translation = Translation.create(text)

        for event in changes:
            if isinstance(event, TranslationRequested):
                assert translation.text == event.text
            elif isinstance(event, TranslationPending):
                translation.apply(event)
                assert translation.translation_id == event.translation_id
            elif isinstance(event, TranslationFinished):
                translation.apply(event)
                assert translation.translated_text == event.translated_text
        assert translation.status == constants._valid_status[len(changes) - 1]

    @given(changes=invalid_translation_changes())
    def test_apply_invalid_changes_raises_invalid_status(self, changes):
        translation = Translation.create('')

        with pytest.raises(InvalidStatusError):
            for event in changes:
                translation.apply(event)
