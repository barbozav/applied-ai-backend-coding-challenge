from functools import singledispatch

from attr import attrib, attrs

from challenge.domain.model.base import Aggregate, Event
from challenge.domain.model.errors import InvalidEventError, InvalidStatusError
from challenge.utils.logging import logger


@attrs(frozen=True)
class TranslationRequested(Event):
    """Event applied when the application client requests a translation.

    Attributes:
        text (str): The text sent to the translation service.

    """

    text = attrib(type=str)


@attrs(frozen=True)
class TranslationPending(Event):
    """Event applied when the application receives a service response.

    Attributes:
        translation_id (int): The translation service id to track the
            translation request.

    """

    translation_id = attrib(type=int)


@attrs(frozen=True)
class TranslationFinished(Event):
    """Event applied when the service finishes translating a text.

    Attributes:
        translated_text (str): The translated text returned from the
            translation service.

    """

    translated_text = attrib(type=str)


@attrs(frozen=True)
class TranslationAborted(Event):
    """Event applied when the application or service aborts a request.

    Attributes:
        error (str): The cause of the aborted translation.

    """

    error = attrib(type=str)


class Translation(Aggregate):
    """Translation aggregate.

    Attributes:
        text (str): The text sent to the translation service.
        translation_id (int): The translation service id to track the
            translation request.
        translated_text (str): The translated text returned from the
            translation service.
        finished (bool): If the translation is still in processing.
        status (str): The current translation status.

    """

    @classmethod
    def create(cls, text):
        """Create a new translation.

        Args:
            text (str): The text to send tp the translation service.

        Returns:
            Translation: The new translation.

        """
        logger.info(f'creating aggregate')
        event = TranslationRequested.create(text)
        instance = super().create([event])
        instance.finished = False
        return instance

    def trigger(self, event):
        """Trigger an event action to the aggregate.

        It uses the `singledispatch` decorator to decide which action
        to take based on the translation Event class input.

        Args:
            event (Event): An event.

        """

        @singledispatch
        def _trigger(_event):
            raise InvalidEventError(f'Invalid event: {_event}')

        @_trigger.register(TranslationRequested)
        def _(_event):
            if self.status != '':
                raise InvalidStatusError(
                    f'Invalid status transition: {self.status}->requested')
            self.text = _event.text
            self.status = 'requested'

        @_trigger.register(TranslationPending)
        def _(_event):
            if self.status != 'requested':
                raise InvalidStatusError(
                    f'Invalid status transition: {self.status}->pending')
            self.translation_id = _event.translation_id
            self.status = 'pending'

        @_trigger.register(TranslationFinished)
        def _(_event):
            if self.status != 'pending':
                raise InvalidStatusError(
                    f'Invalid status transition: {self.status}->finished')
            self.translated_text = _event.translated_text
            self.status = 'finished'
            self.finished = True

        @_trigger.register(TranslationAborted)
        def _(_event):
            self.error = _event.error
            self.status = 'aborted'
            self.finished = True

        logger.info(f'applying event ({event.id}) on aggregate: {self.id}')
        logger.debug(event.as_dict())

        _trigger(event)
