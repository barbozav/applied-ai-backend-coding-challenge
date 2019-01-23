import pytest
from hypothesis import given

from challenge.domain.model.translation import Translation
from challenge.domain.repositories import AggregatesRepository
from challenge.persistence import create_db, create_tables
from challenge.persistence.eventstore import model as e_model  # noqa: F401
from challenge.persistence.eventstore.postgresql import PostgresEventStore
from tests.fixtures.strategies import valid_translation, valid_translation_list


class TestRepositories:
    @pytest.fixture
    def repository(self):
        db = create_db()
        create_tables(db)
        return AggregatesRepository(Translation, PostgresEventStore())

    @given(translation=valid_translation())
    def test_save_persists_translation_aggregate(self, repository,
                                                 translation):
        repository.save(translation)
        aggregate = repository.get(translation.id)

        assert isinstance(aggregate, Translation)
        assert aggregate.id == translation.id
        assert aggregate.status == translation.status
        assert aggregate.changes == translation.changes

    @given(translations=valid_translation_list())
    def test_get_returns_translation_aggregate(self, repository, translations):
        for translation in translations:
            repository.save(translation)

        for translation in translations:
            aggregate = repository.get(translation.id)
            assert isinstance(aggregate, Translation)
            assert aggregate.id == translation.id
            assert aggregate.status == translation.status
            assert aggregate.changes == translation.changes
