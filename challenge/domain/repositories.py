from challenge.domain.model import translation
from challenge.persistence import session_scope
from challenge.utils.logging import logger


class AggregatesRepository:
    """Interface between the application layer and persistence layer.

    It translates the domain layer models to persistence data models.

    For now we have a Translation aggregate and PostgresEventstore, but
    it could be expanded to other entities as a TextSummarization
    aggregate and MongoEventstore.

    Args:
        aggregate_cls (class): The aggregate class.
        event_store (EventStore): The persisted event store.

    """

    def __init__(self, aggregate_cls, event_store):
        self._aggregate_cls = aggregate_cls
        self._event_store = event_store

    def get(self, aggregate_uuid):
        """Get an aggregate from the event store.

        Given an UUID, it loads an event stream and re-constructs each
        event row into an Event object given its class.

        Then it constructs an aggregate with the given UUID and the
        event stream version, applying to it the re-constructed events.

        This method is responsible for both managing the persistence
        session and queries as well as translating data to domain
        objects.

        Args:
            aggregate_uuid (str): An UUID4 string. The aggregate from
                which query the event stream.

        Returns:
            Aggregate: In fact, it instantiates an Aggregate of its
                `self._aggregate_cls` with applied events from the
                stream.

        """
        logger.info(f'loading aggregate: {aggregate_uuid}...')
        with session_scope() as session:
            events_stream = self._event_store.load_stream(
                session, aggregate_uuid)
            stream_events = self._event_row_to_object(events_stream.events)

            aggregate = self._aggregate_cls(aggregate_uuid,
                                            events_stream.version)

            for event in stream_events:
                aggregate.apply(event)

        return aggregate

    def save(self, aggregate):
        """Save an aggregate into the event store.

        Args:
            aggregate (Aggregate): Aggregate which attributes will be
                passed as arguments to the persisted data model to
                append events to the stream.

        """
        logger.info(f'saving aggregate: {aggregate.id}...')
        with session_scope() as session:
            self._event_store.append_to_stream(
                session, aggregate.id, aggregate.version, aggregate.changes)

    def _event_row_to_object(self, event_rows):
        event_objects = []
        for row in event_rows:
            # Get the class in the `event` column from the translation model.
            event_cls = getattr(translation, row.event)
            kwargs = row.data

            instance = event_cls(**kwargs)

            event_objects.append(instance)

        return event_objects
