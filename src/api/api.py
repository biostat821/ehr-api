"""HTTP API."""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Generator

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

import database
from api.models import InputLab, InputPatient, Lab, Patient
from dao import NotFoundError
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
from dao.patient_dao import PatientDao

database_path = "sqlite:///my_db.db"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Set up and tear down database."""
    database.setup(database_path)
    yield
    pass


app = FastAPI(lifespan=lifespan)


def get_engine() -> Engine:
    """Generate database engine."""
    return create_engine(database_path, isolation_level="SERIALIZABLE")


def get_patient_dao(engine: Engine = Depends(get_engine)) -> PatientDao:
    """Generate patient DAO."""
    return PatientDao(engine)


def get_lab_dao(engine: Engine = Depends(get_engine)) -> LabDao:
    """Generate lab DAO."""
    return LabDao(engine)


def get_session(
    engine: Engine = Depends(get_engine),
) -> Generator[Session, None, None]:
    """Generate a database session."""
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
    patient_dao: PatientDao = Depends(get_patient_dao),
    lab_dao: LabDao = Depends(get_lab_dao),
    session: Session = Depends(get_session),
) -> Lab:
    """Create a lab."""
    try:
        storage_patient = patient_dao._read(patient_id, session)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    storage_lab = lab_dao._create(
        patient_id=patient_id,
        admission_number=lab.admission_number,
        datetime=lab.datetime,
        name=lab.name,
        value=lab.value,
        units=lab.units,
        session=session,
    )
    storage_patient.labs.append(storage_lab)
    return Lab.from_storage(storage_lab)


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
