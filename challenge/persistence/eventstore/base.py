from abc import ABC, abstractmethod

from attr import attrib, attrs


@attrs
class EventStream:
    """Event stream.

    Attributes:
        version (int): Event stream version for optimistic locking.
        events ([Event]): List of events.

    """

    version = attrib()
    events = attrib()


class EventStore(ABC):
    """Base event store."""

    @abstractmethod
    def load_stream(self, uuid):
        """Get an event stream from the database.

        Args:
            aggregate_uuid (str): The aggregate UUID4 string from which
                to get the event stream.

        Returns:
            EventStream: An event stream.

        """
        pass

    @abstractmethod
    def append_to_stream(self, uuid, version, events):
        """Append a list of events to an event stream.

        Args:
            aggregate_uuid (str): The aggregate UUID4 string in which to
                append the events.
            version (int): The expected event stream version to grant
                consistency through optimist locking.
            events ([Events]): A list of events to be appended.

        Returns:
            EventStream: An event stream.

        """
        pass
