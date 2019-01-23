from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
from hypothesis import given

from challenge.domain.model.base import Aggregate, Event
from tests.fixtures import constants
from tests.fixtures.strategies import valid_base_event_list


class TestEvent:
    @patch('uuid.uuid4', return_value=constants.UUID4)
    def test_create_returns_event(self, mock_uuid4):
        event = Event.create()
        assert isinstance(event, Event)

    @patch('uuid.uuid4', return_value=constants.UUID4)
    def test_create_sets_attributes(self, mock_uuid4):
        with freeze_time(constants.NOW):
            event = Event.create()
            assert event.id == constants.UUID4
            assert event.occurred_at == constants.NOW


@patch.multiple(Aggregate, __abstractmethods__=set())
class TestAggregate:
    def test_create_returns_aggregate(self):
        aggregate = Aggregate.create([])
        assert isinstance(aggregate, Aggregate)

    @given(events=valid_base_event_list())
    def test_create_sets_attributes(self, events):
        with patch('uuid.uuid4', return_value=constants.UUID4):
            aggregate = Aggregate.create(events)
            assert aggregate.id == constants.UUID4
            assert aggregate.version is None
            assert aggregate.changes == events

    @given(events=valid_base_event_list())
    @patch('challenge.domain.model.base.Aggregate.apply')
    def test_create_applies_changes(self, aggregate_apply, events):
        aggregate = Aggregate.create(events)  # noqa: F841
        assert aggregate_apply.call_count == len(events)
