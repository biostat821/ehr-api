"""Tests for lab_dao.py."""

from datetime import datetime

import pytest
from dao import NotFoundError
from dao.lab_dao import LabDao
from dao.models import Base
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool


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
    lab_dao = LabDao(db_engine)

    with pytest.raises(NotFoundError, match=r"No lab found"):
        _ = lab_dao.read("does_not_exist")


def test_read_exists_succeeds(db_engine: Engine) -> None:
    """Test read() when the lab exists."""
    lab_dao = LabDao(db_engine)
    created = lab_dao.create(
        patient_id="Alice",
        admission_number=0,
        datetime=datetime.now(),
        name="lab_name",
        value=0.0,
        units="meters",
    )
    _ = lab_dao.create(
        patient_id="Bob",
        admission_number=0,
        datetime=datetime.now(),
        name="lab_name",
        value=0.0,
        units="meters",
    )

    retrieved = lab_dao.read(created.id)

    assert retrieved.name == created.name


def test_list_succeeds(db_engine: Engine) -> None:
    """Test list()."""
    lab_dao = LabDao(db_engine)
    _ = lab_dao.create(
        patient_id="Alice",
        admission_number=0,
        datetime=datetime(2016, 10, 17),
        name="lab_name",
        value=0.0,
        units="meters",
    )
    _ = lab_dao.create(
        patient_id="Alice",
        admission_number=0,
        datetime=datetime(2019, 4, 2),
        name="lab_name",
        value=0.0,
        units="meters",
    )

    retrieved = lab_dao.list()

    assert len(retrieved) == 2
