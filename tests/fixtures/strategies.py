from string import ascii_letters, digits, printable

from hypothesis.strategies import (composite, integers, just, lists,
                                   sampled_from, text)

from challenge.domain.model.base import Event
from challenge.domain.model.translation import (
    Translation, TranslationAborted, TranslationFinished, TranslationPending,
    TranslationRequested)

alphanum = ascii_letters + digits


@composite
def valid_id(draw):
    """Draw a valid valid text.
    Returns:
        str: A random string containing 0 or more characters.
    """
    return draw(text(alphanum))


@composite
def valid_text(draw):
    """Draw a valid valid text.
    Returns:
        str: A random string containing 0 or more characters.
    """
    return draw(text(printable))


@composite
def valid_base_event_list(draw):
    """Draw a valid list of base events.
    Returns:
        [Event]: A list containing 0 or more base Events.
    """
    changes = draw(lists(just(Event.create())))
    return changes


@composite
def valid_translation_requested_event(draw):
    text = draw(valid_text())
    requested = TranslationRequested.create(text)
    return requested


@composite
def valid_translation_pending_event(draw):
    translation_id = draw(valid_id())
    pending = TranslationPending.create(translation_id)
    return pending


@composite
def valid_translation_finished_event(draw):
    translated_text = draw(valid_text())
    finished = TranslationFinished.create(translated_text)
    return finished


@composite
def valid_translation_changes(draw):
    """Draw a valid list of base events.
    Returns:
        [Event]: A list containing 0 or more base Events.
    """
    requested = draw(valid_translation_requested_event())
    pending = draw(valid_translation_pending_event())
    finished = draw(valid_translation_finished_event())

    changes = draw(
        sampled_from([[requested], [requested, pending],
                      [requested, pending, finished]]))

    return changes


@composite
def invalid_translation_changes(draw):
    """Draw a valid list of base events.
    Returns:
        [Event]: A list containing 0 or more base Events.
    """
    requested = draw(valid_translation_requested_event())
    pending = draw(valid_translation_pending_event())
    finished = draw(valid_translation_finished_event())

    changes = draw(
        sampled_from([[requested], [finished], [pending, requested],
                      [pending, pending]]))

    return changes


@composite
def valid_translation(draw):
    """Draw a valid translation.
    Returns:
        Translation: A valid Translation aggregate.
    """
    text = draw(valid_text())
    translation = Translation.create(text)
    changes = draw(valid_translation_changes())
    for event in changes:
        if isinstance(event, TranslationRequested):
            continue
        translation.apply(event)
    return translation


@composite
def valid_translation_list(draw):
    """Draw a valid translation.
    Returns:
        Translation: A valid Translation aggregate.
    """
    translations = draw(lists(valid_translation()))
    return translations
