"""Tests for patient_dao.py."""

from datetime import datetime

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from dao import NotFoundError
from dao.models import Base
from dao.patient_dao import PatientDao


@pytest.fixture
def db_engine() -> Engine:
    """Generate database engine."""
    database_path = "sqlite:///"
    engine = create_engine(
        database_path,
        isolation_level="SERIALIZABLE",
        # https://fastapi.tiangolo.com/tutorial/sql-databases/#note
        # https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine


def test_read_empty_table_raises(db_engine: Engine) -> None:
    """Test read() with and empty table."""
    dao = PatientDao(db_engine)

    with pytest.raises(NotFoundError, match=r"No patient found"):
        _ = dao.read("does_not_exist")


def test_read_exists_succeeds(db_engine: Engine) -> None:
    """Test read() when the patient exists."""
    dao = PatientDao(db_engine)
    created = dao.create(date_of_birth=datetime(2016, 10, 17))
    _ = dao.create(date_of_birth=datetime(2019, 4, 2))

    retrieved = dao.read(created.id)

    assert retrieved.date_of_birth == created.date_of_birth


def test_list_succeeds(db_engine: Engine) -> None:
    """Test list()."""
    dao = PatientDao(db_engine)
    _ = dao.create(date_of_birth=datetime(2016, 10, 17))
    _ = dao.create(date_of_birth=datetime(2019, 4, 2))

    retrieved = dao.list()

    assert len(retrieved) == 2
