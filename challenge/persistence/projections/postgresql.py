from dynaconf import settings
from sqlalchemy.sql import text

from challenge.persistence.projections.model import TranslationModel
from challenge.utils.logging import logger


class PostgresTranslation:
    """PostgreSQL queries for the "translations" table."""

    def get(self, session, page=1, per_page=None):
        """Query "translations" rows ordered and limited by pagination.

        Args:
            session (Session): A session context into which operate.
            page (int): The page number to set the query offset.
            per_page (int): The number of rows per page to limit the
                query.

        Returns:
            Query: `per_page` rows ordered by `translated_text`
                ascending.

        """
        per_page = per_page or settings.TRANSLATIONS_PER_PAGE

        return session.query(TranslationModel).order_by(
            TranslationModel.length.asc()).limit(
                settings.TRANSLATIONS_PER_PAGE).offset(
                    (page - 1) * settings.TRANSLATIONS_PER_PAGE)

    def count(self, session):
        """Count the number of "translations" rows.

        Args:
            session (Session): A session context into which operate.

        Returns:
            int: number of rows in the "translations" table.

        """
        return session.query(TranslationModel).count()

    def insert_or_update(self,
                         session,
                         aggregate_uuid,
                         status,
                         original_text,
                         translated_text=None):
        """Insert or update an aggregate in the "translations" table.

        Args:
            session (Session): A session context into which operate.
            aggregate_uuid (str): An UUID4 string. It must match its
                respective event sourced aggregate.
            text (str): The text sent to the translation service.
            status (str): The translation processing status.
            translated_text (str): The text received from the
                translation service.

        """
        if status == 'requested':
            sql = text(
                f'INSERT INTO translations (uuid, status, length, text) '
                f'VALUES (:uuid, :status, :length, :text) ON CONFLICT DO NOTHING'
            )
            values = {
                'uuid': aggregate_uuid,
                'status': 'requested',
                'length': 0,
                'text': original_text
            }

        elif status == 'pending':
            sql = text(f"UPDATE translations "
                       f"SET status = 'pending' "
                       f"WHERE uuid = :aggregate_uuid")
            values = {'aggregate_uuid': aggregate_uuid}

        elif status == 'finished':
            sql = text(f"UPDATE translations "
                       f"SET status = 'finished', "
                       f"length = {len(translated_text)}, "
                       f"translated_text = :translated_text "
                       f"WHERE uuid = :aggregate_uuid")
            values = {
                'aggregate_uuid': aggregate_uuid,
                'translated_text': translated_text
            }

        logger.debug(sql)
        session.execute(sql, values)
