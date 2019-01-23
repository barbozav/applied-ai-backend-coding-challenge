import math

from attr import attrib, attrs
from dynaconf import settings

from challenge.domain.model.translation import Translation
from challenge.domain.repositories import AggregatesRepository
from challenge.persistence import session_scope
from challenge.persistence.eventstore.postgresql import PostgresEventStore
from challenge.utils.logging import logger


@attrs(frozen=True)
class Pagination:
    """A simple pagination helper.

    Attributes:
        items (Query): "translations" table queried rows.
        total (int): "translations" table total count of rows.
        page (int): Instance page.

    """

    items = attrib()
    total = attrib()
    page = attrib()

    @property
    def has_prev(self):
        """Return true if there's a previous page."""
        return self.page > 1

    @property
    def prev_page(self):
        """Return the previous page number if it exists."""
        return self.page - 1 if self.has_prev else None

    @property
    def has_next(self):
        """Return true if there's a next page."""
        limit = self.page * settings.TRANSLATIONS_PER_PAGE
        return limit < self.total

    @property
    def next_page(self):
        """Return the next page number if it exists."""
        return self.page + 1 if self.has_next else None

    @property
    def last_page(self):
        """Return the last page."""
        return math.ceil(self.total / settings.TRANSLATIONS_PER_PAGE)


class TranslationProjections:
    """Interface between the application layer and persistence layer.

    It translates the domain layer models to persistence data models.

    For now we have a Translation projection for visualization, but it
    could be expanded for other projections as auditing or data
    analysis.

    Args:
        read_model: The translations projection (read-model).

    """

    def __init__(self, read_model):
        self._read_model = read_model
        self._repository = AggregatesRepository(Translation,
                                                PostgresEventStore())

    def get(self, page=1):
        """Get translation items from a single page.

        Args:
            page (int): Page number.

        Returns:
            Pagination: a `Pagination` instance with the translation
                items and pagination properties.

        """
        with session_scope() as session:
            total = self._read_model.count(session)
            items = self._read_model.get(session, page)

        return Pagination(items=items, total=total, page=page)

    def update(self, aggregate_uuid):
        """Update a translation from the aggregates repository.

        Args:
            aggregate_uuid (str): An UUID4 string to which aggregate
                projection should be update.

        """
        translation = self._repository.get(aggregate_uuid)

        status = translation.status
        text = translation.text
        if status == 'finished':
            translated_text = translation.translated_text
        else:
            translated_text = None

        logger.info(f'updating projection: {aggregate_uuid}')
        with session_scope() as session:
            self._read_model.insert_or_update(session, aggregate_uuid, status,
                                              text, translated_text)
