"""Tests for api.py."""
import datetime

import pytest
from api.api import app, get_engine
from dao.lab_dao import LabDao
from dao.models import Base
from dao.patient_dao import PatientDao
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_engine() -> Engine:
    """Generate database engine, as pytest fixture."""
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


@pytest.fixture
def client(db_engine: Engine) -> TestClient:
    """Generate test client."""
    app.dependency_overrides[get_engine] = lambda: db_engine

    return TestClient(app)


def test_read_patient_empty_404(client: TestClient) -> None:
    """Test read_patient."""
    response = client.get("/patients/foo")
    assert response.status_code == 404


def test_create_patient_succeeds(client: TestClient) -> None:
    """Test create_patient."""
    response = client.post(
        "patients/",
        json={
            "date_of_birth": "2016-10-17T00:00:00",
            "gender": "male",
            "language": "English",
            "marital_status": "married",
            "race": "White",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    for key, value in {
        "date_of_birth": "2016-10-17T00:00:00",
        "gender": "male",
        "language": "English",
        "marital_status": "married",
        "race": "White",
    }.items():
        assert payload[key] == value


def test_read_patient_exists_200(
    db_engine: Engine, client: TestClient
) -> None:
    """Test read_patient."""
    dao = PatientDao(db_engine)
    created = dao.create(date_of_birth=datetime.datetime(2016, 10, 17))

    response = client.get(f"patients/{created.id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "date_of_birth": "2016-10-17T00:00:00",
        "id": created.id,
        "gender": "unknown",
        "language": "unknown",
        "marital_status": "unknown",
        "race": "unknown",
    }


def test_list_patients_empty_empty(client: TestClient) -> None:
    """Test list_patients."""
    response = client.get("/patients")
    assert response.status_code == 200
    assert response.json() == []


def test_list_patients_exists_succeeds(
    db_engine: Engine, client: TestClient
) -> None:
    """Test list_patients."""
    dao = PatientDao(db_engine)
    dao.create(date_of_birth=datetime.datetime(2016, 10, 17))

    response = client.get("/patients")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_labs_exists_succeeds(
    db_engine: Engine, client: TestClient
) -> None:
    """Test list_labs."""
    patient_dao = PatientDao(db_engine)
    patient = patient_dao.create(date_of_birth=datetime.datetime(2016, 10, 17))
    lab_dao = LabDao(db_engine)
    lab_dao.create(
        patient_id=patient.id,
        admission_number=0,
        datetime=datetime.datetime.now(),
        name="lab_name",
        value=0.0,
        units="meters",
    )

    response = client.get(f"patients/{patient.id}")
    assert response.status_code == 200
    response = client.get(f"/patients/{patient.id}/labs")
    assert response.status_code == 200
    assert len(response.json()) == 1
