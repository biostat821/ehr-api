"""Tests for api.py."""
import datetime

from api.api import app
from dao.lab_dao import LabDao
from dao.patient_dao import PatientDao
from fastapi.testclient import TestClient

client = TestClient(app)


def test_read_patient_empty_404() -> None:
    """Test read_patient."""
    dao = PatientDao("sqlite:///my_db.db")
    dao.drop_table()
    dao.create_table()

    response = client.get("/patients/foo")
    assert response.status_code == 404


def test_create_patient_succeeds() -> None:
    """Test create_patient."""
    dao = PatientDao("sqlite:///my_db.db")
    dao.drop_table()
    dao.create_table()

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


def test_read_patient_exists_200() -> None:
    """Test read_patient."""
    dao = PatientDao("sqlite:///my_db.db")
    dao.drop_table()
    dao.create_table()
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


def test_list_patients_empty_empty() -> None:
    """Test list_patients."""
    dao = PatientDao("sqlite:///my_db.db")
    dao.drop_table()
    dao.create_table()

    response = client.get("/patients")
    assert response.status_code == 200
    assert response.json() == []


def test_list_patients_exists_succeeds() -> None:
    """Test list_patients."""
    dao = PatientDao("sqlite:///my_db.db")
    dao.drop_table()
    dao.create_table()
    dao.create(date_of_birth=datetime.datetime(2016, 10, 17))

    response = client.get("/patients")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_labs_exists_succeeds() -> None:
    """Test list_labs."""
    patient_dao = PatientDao("sqlite:///my_db.db")
    patient_dao.drop_table()
    patient_dao.create_table()
    patient = patient_dao.create(date_of_birth=datetime.datetime(2016, 10, 17))
    lab_dao = LabDao("sqlite:///my_db.db")
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
