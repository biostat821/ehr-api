"""Tests for patient_dao.py."""
from datetime import datetime

import pytest
from dao.patient_dao import NotFoundError, PatientDao


def test_read_empty_table_raises() -> None:
    """Test read() with and empty table."""
    dao = PatientDao("sqlite:///")
    dao.create_table()

    with pytest.raises(NotFoundError, match=r"No patient found"):
        _ = dao.read("does_not_exist")


def test_read_exists_succeeds() -> None:
    """Test read() when the patient exists."""
    dao = PatientDao("sqlite:///")
    dao.create_table()
    created = dao.create(date_of_birth=datetime(2016, 10, 17))
    _ = dao.create(date_of_birth=datetime(2019, 4, 2))

    retrieved = dao.read(created.id)

    assert retrieved.date_of_birth == created.date_of_birth


def test_list_succeeds() -> None:
    """Test list()."""
    dao = PatientDao("sqlite:///")
    dao.create_table()
    _ = dao.create(date_of_birth=datetime(2016, 10, 17))
    _ = dao.create(date_of_birth=datetime(2019, 4, 2))

    retrieved = dao.list()

    assert len(retrieved) == 2
