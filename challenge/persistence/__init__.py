from contextlib import contextmanager

import sqlalchemy
from dynaconf import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()


def create_db(uri=None):
    """Create SQLAlchemy database engine and Session binding."""
    uri = uri or settings.DATABASE_URI
    db = sqlalchemy.create_engine(uri)
    Session.configure(bind=db)
    return db


def create_tables(db):
    """Create all database tables."""
    Base.metadata.create_all(db)


@contextmanager
def session_scope():
    """Session context for application interface with database."""
    session = Session()
    try:
        yield session
        session.commit()
    except:  # noqa: E722
        session.rollback()
        raise
    finally:
        session.close()
