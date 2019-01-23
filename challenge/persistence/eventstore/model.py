from sqlalchemy import JSON, VARCHAR, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from challenge.persistence import Base


class AggregateModel(Base):
    """SQLAlchemy model for aggregates.

    This table is a write-model for the event sourced aggregates.

    It represents a single aggregate and holds an event stream version,
    which is related to 0 or more events (1-N).

    Attributes:
        uuid (VARCHAR): Primary key, `aggregate` and event-stream
            identifier.
        version (Integer): Event stream version for optimistic lock.
        events ([Event]): A list of events.

    """

    __tablename__ = 'aggregates'

    uuid = Column(VARCHAR(36), primary_key=True)
    version = Column(Integer, default=1)


class EventModel(Base):
    """SQLAlchemy model for events.

    This table is a write-model for the events.

    It represents a single event in a single event stream - this event
    relates to a single aggregate (1-1).

    Attributes:
        uuid (VARCHAR): Primary key, event identifier.
        aggregate_uuid (VARCHAR): Foreign key, aggregate identifier.
        event (VARCHAR): The event class name.
        data (JSON): A JSON dictionary with the event attributes.
        aggregate (Aggregate): The aggregate it relates to.

    """

    __tablename__ = 'events'

    uuid = Column(VARCHAR(36), primary_key=True)
    aggregate_uuid = Column(VARCHAR(36), ForeignKey('aggregates.uuid'))
    event = Column(VARCHAR(36))
    data = Column(JSON)
    aggregate = relationship(AggregateModel, backref='events')
