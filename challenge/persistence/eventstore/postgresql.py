import json

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text

from challenge.persistence.eventstore.base import EventStore, EventStream
from challenge.persistence.eventstore.errors import (ConcurrencyError,
                                                     NotFoundError, WriteError)
from challenge.persistence.eventstore.model import AggregateModel
from challenge.utils.logging import logger


class PostgresEventStore(EventStore):
    """PostgreSQL queries for an event store.

    It handles event streams (querying aggregates and events
    accordingly).
    """

    def load_stream(self, session, aggregate_uuid):
        """Query an event stream from an aggregate.

        Args:
            session (Session): A session context into which operate.
            aggregate_uuid (str): An UUID4 string. The aggregate from
                which query the events.

        Returns:
            Query: A Query with rows from the "events" table.

        """
        try:
            aggregate = session.query(AggregateModel).options(
                joinedload('events')).filter(
                    AggregateModel.uuid == str(aggregate_uuid)).one()
        except NoResultFound:
            raise NotFoundError(f'Aggregate not found: {aggregate_uuid}')

        version = aggregate.version
        events = aggregate.events
        event_stream = EventStream(version, events)

        logger.debug(event_stream)

        return event_stream

    def append_to_stream(self, session, aggregate_uuid, expected_version,
                         events):
        """Append an event stream from an aggregate.

        Args:
            session (Session): A session context into which operate.
            aggregate_uuid (str): An UUID4 string. The aggregate from
                which query the events.
            expected_version (int): Version for optimistic lock. Before
                appending an event to an event stream, its aggregate
                must be loaded to avoid inconsistencies. Then, the
                `expected_version` is set and verified to make sure no
                other session will be able to alter the same aggregate
                at the same time.
            events ([Event]): List of events to append to the event
                stream. They will be converted to a dict formatted as a
                JSON before the operation.

        """
        if expected_version:
            # If an `expected_version` is given, the aggregate must be
            # updated as it is already in some version.
            sql = text(f"UPDATE aggregates "
                       f"SET version = :expected_version + 1 "
                       f"WHERE version = :expected_version "
                       f"AND uuid = :aggregate_uuid")
            values = {
                'expected_version': expected_version,
                'aggregate_uuid': aggregate_uuid
            }

            logger.debug(sql, values)
            result = session.execute(sql, values)

            if result.rowcount != 1:
                raise ConcurrencyError(
                    'Failed to update aggregate in database.')

        else:
            # Or else it's a new aggregate.
            sql = text(f"INSERT INTO aggregates (uuid, version) "
                       f"VALUES (:aggregate_uuid, 1)")
            values = {'aggregate_uuid': aggregate_uuid}

            logger.debug(sql)
            result = session.execute(sql, values)

            if result.rowcount != 1:
                raise WriteError('Failed to insert aggregate into database.')

        for event in events:
            # Iterate through events and trying to add them to "events" table,
            # relating each and every one with the same aggregate. But, in the
            # occasion an event is already there (based on its UUID column),
            # it's dropped (`DO NOTHING`).

            sql = text(
                f"INSERT INTO events (uuid, aggregate_uuid, event, data) "
                f"VALUES (:uuid,:aggregate_uuid,:event,:data) ON CONFLICT (uuid) DO NOTHING"
            )
            values = {
                'uuid': event.id,
                'aggregate_uuid': aggregate_uuid,
                'event': event.__class__.__name__,
                'data': json.dumps(event.as_dict())
            }

            result = session.execute(sql, values)

            logger.debug(sql)
            if result.rowcount:
                logger.info(f'new event: {event.id}')
            else:
                logger.debug(f'no new event')
