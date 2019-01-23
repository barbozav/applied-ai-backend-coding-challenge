from sqlalchemy import TEXT, VARCHAR, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from challenge.persistence import Base
from challenge.persistence.eventstore.model import AggregateModel


class TranslationModel(Base):
    """SQLAlchemy model for "translations" projection table.

    This table is a read-model for the visualization of translation data
    in the application layer.

    As it's created based on data from the event stores, it doesn't need
    to be updated in real-time and if smething goes wrong it's perfectly
    fine to re-create it.

    Attributes:
        uuid (VARCHAR): Primary key and foreign key, as this model is a
            projection of an `aggregate`. Both share the same `uuid` in
            different tables.
        status (VARCHAR): Translation processing status ("requested" as
            soon as the application receives it from the client,
            "pending" whenever the translation service responds with
            tracking information and "finished" when the service is done
            with the processing. In case of failure, there's an
            "aborted" status as well.)
        length (Integer): The `translated_text` length for ordering when
            querying for the application frontend.
        text (TEXT): The text sent to the translation service.
        translated_text (TEXT): The translated text returned from the
            translation service.
        aggregate (Aggregate): This projection respective write-model,
            an `aggregate` in a relation of 1-1.

    """

    __tablename__ = 'translations'

    uuid = Column(
        VARCHAR(36),
        ForeignKey('aggregates.uuid'),
        primary_key=True,
    )
    status = Column(VARCHAR(16))
    length = Column(Integer)
    text = Column(TEXT)
    translated_text = Column(TEXT)
    aggregate = relationship(AggregateModel)
