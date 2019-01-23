import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from attr import asdict, attrib, attrs


@attrs(frozen=True)
class Event(ABC):
    """Base event.

    Attributes:
        id (str): An UUID4 string representing a particular event.
        occurred_at (str): Event occurence timestamp.

    """

    id = attrib()
    occurred_at = attrib()

    @classmethod
    def create(cls, *args, **kwargs):
        """Create a new event.

        It generates a new UUID4 and timestamp.

        Args:
            *args (list): Event positional arguments.
            **kwargs (dict): Event keywords arguments.

        Returns:
            Event: A new event.

        """
        event_uuid = str(uuid.uuid4())
        occurred_at = datetime.utcnow().isoformat()
        return cls(event_uuid, occurred_at, *args, **kwargs)

    def as_dict(self):
        """Represent the Event as a dictionary.

        Convert instance attributes to Python dictionary keys and
        values.

        """
        return asdict(self)


class Aggregate(ABC):
    """Base aggregate.

    Holds its own attributes and a list of applied changes (`Events`).

    Args:
        aggregate_uuid (str): An UUID4 string.
        version (int): Optimistic locking event stream version.
        events ([Event]): List of events to apply.
        status (str): Aggregate status to be set.
    """

    def __init__(self, aggregate_uuid, version=None):
        self._id = aggregate_uuid
        self._version = version
        self._changes = []

        self.status = ''

    @property
    def id(self):
        """Return aggregate UUID."""
        return self._id

    @property
    def version(self):
        """Return aggregate version."""
        return self._version

    @property
    def changes(self):
        """Return aggregate applied changes list."""
        return self._changes

    @classmethod
    def create(cls, events):
        """Create a new aggregate.

        It generates a new UUID and applies initial events to the newly
        created instance

        Args:
            events ([Event]): Events to apply to the new aggregate.

        Returns:
            Aggregate: A new aggregate.

        """
        aggregate_uuid = str(uuid.uuid4())

        instance = cls(aggregate_uuid)

        for event in events:
            instance.apply(event)

        return instance

    def apply(self, event):
        """Apply change to aggregate.

        Args:
            event (Event): An event change to apply.

        """
        self.trigger(event)
        self._changes.append(event)

    @abstractmethod
    def trigger(self, event):
        """Trigger an event action to the aggregate.

        Args:
            event (Event): An event.

        """
        pass
