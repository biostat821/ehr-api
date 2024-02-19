"""Tests for lab_dao.py."""
from datetime import datetime

import pytest
from dao import NotFoundError
from dao.lab_dao import LabDao


def test_read_empty_table_raises() -> None:
    """Test read() with and empty table."""
    lab_dao = LabDao("sqlite:///")
    lab_dao.create_table()

    with pytest.raises(NotFoundError, match=r"No lab found"):
        _ = lab_dao.read("does_not_exist")


def test_read_exists_succeeds() -> None:
    """Test read() when the lab exists."""
    lab_dao = LabDao("sqlite:///")
    lab_dao.create_table()
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


def test_list_succeeds() -> None:
    """Test list()."""
    lab_dao = LabDao("sqlite:///")
    lab_dao.create_table()
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
