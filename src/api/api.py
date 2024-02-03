"""HTTP API."""
from typing import Generator

from api.models import InputLab, InputPatient, Lab, Patient
from dao.lab_dao import LabDao
from dao.models import (
    Gender as StorageGender,
)
from dao.models import (
    Language as StorageLanguage,
)
from dao.models import (
    MaritalStatus as StorageMaritalStatus,
)
from dao.models import (
    Race as StorageRace,
)
from dao.patient_dao import NotFoundError, PatientDao
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

app = FastAPI()


def get_patient_dao() -> PatientDao:
    """Generate patient DAO."""
    return PatientDao("sqlite:///my_db.db")


def get_lab_dao() -> LabDao:
    """Generate lab DAO."""
    return LabDao("sqlite:///my_db.db")


def get_session() -> Generator[Session, None, None]:
    """Generate a database session."""
    database_path = "sqlite:///my_db.db"
    engine = create_engine(database_path, isolation_level="SERIALIZABLE")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        yield session


@app.post("/patients")
async def create_patient(
    patient: InputPatient,
    patient_dao: PatientDao = Depends(get_patient_dao),
    session: Session = Depends(get_session),
) -> Patient:
    """Create a patient."""
    return Patient.from_storage(
        patient_dao._create(
            date_of_birth=patient.date_of_birth,
            gender=StorageGender(patient.gender),
            language=StorageLanguage(patient.language),
            marital_status=StorageMaritalStatus(patient.marital_status),
            race=StorageRace(patient.race),
            session=session,
        )
    )


@app.post("/patients/{patient_id}/labs")
async def create_lab(
    patient_id: str,
    lab: InputLab,
    lab_dao: LabDao = Depends(get_lab_dao),
    session: Session = Depends(get_session),
) -> Lab:
    """Create a lab."""
    return Lab.from_storage(
        lab_dao._create(
            patient_id=patient_id,
            admission_number=lab.admission_number,
            datetime=lab.datetime,
            name=lab.name,
            value=lab.value,
            units=lab.units,
            session=session,
        )
    )


@app.get("/patients")
async def list_patients(
    patient_dao: PatientDao = Depends(get_patient_dao),
    session: Session = Depends(get_session),
) -> list[Patient]:
    """List patients."""
    return [
        Patient.from_storage(patient) for patient in patient_dao._list(session)
    ]


@app.get("/patients/{patient_id}")
async def read_patient(
    patient_id: str,
    verbose: bool = False,
    patient_dao: PatientDao = Depends(get_patient_dao),
    session: Session = Depends(get_session),
) -> Patient:
    """Get a patient by id."""
    print(f"Is verbose: {verbose}")
    try:
        return Patient.from_storage(patient_dao._read(patient_id, session))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/patients/{patient_id}/labs")
async def list_labs(
    patient_id: str,
    patient_dao: PatientDao = Depends(get_patient_dao),
    session: Session = Depends(get_session),
) -> list[Lab]:
    """List patients."""
    try:
        return [
            Lab.from_storage(lab)
            for lab in patient_dao._read(patient_id, session).labs
        ]
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/patients/{patient_id}/labs/{lab_id}")
async def read_lab(
    patient_id: str,
    lab_id: str,
    lab_dao: LabDao = Depends(get_lab_dao),
    session: Session = Depends(get_session),
) -> Lab:
    """Get a lab by id."""
    try:
        lab = Lab.from_storage(lab_dao._read(lab_id, session))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if lab.patient_id != patient_id:
        raise HTTPException(
            status_code=404, detail="Such a lab does not exist"
        )
    return lab
