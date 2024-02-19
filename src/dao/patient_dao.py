"""Patient data access."""
import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import (
    Engine,
    select,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, sessionmaker

from dao import NotFoundError
from dao.models import (
    Gender,
    Language,
    MaritalStatus,
    Patient,
    Race,
)


class PatientDao:
    """Patient data access object."""

    def __init__(self, engine: Engine) -> None:
        """Initialize."""
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create(
        self,
        date_of_birth: datetime,
        gender: Gender = Gender.unknown,
        marital_status: MaritalStatus = MaritalStatus.unknown,
        language: Language = Language.unknown,
        race: Race = Race.unknown,
    ) -> Patient:
        """Create a patient."""
        with self.Session.begin() as session:
            return self._create(
                date_of_birth,
                gender,
                language,
                marital_status,
                race,
                session,
            )

    def _create(
        self,
        date_of_birth: datetime,
        gender: Gender,
        language: Language,
        marital_status: MaritalStatus,
        race: Race,
        session: Session,
    ) -> Patient:
        """Create a patient."""
        id = str(uuid.uuid4())
        patient = Patient(
            id=id,
            date_of_birth=date_of_birth,
            gender=gender,
            marital_status=marital_status,
            language=language,
            race=race,
        )
        session.add(patient)
        session.commit()
        return patient

    def read(self, patient_id: str) -> Patient:
        """Get a patient."""
        with self.Session.begin() as session:
            return self._read(patient_id, session)

    def _read(self, patient_id: str, session: Session) -> Patient:
        """Get a patient in a session."""
        try:
            result = session.scalars(
                select(Patient).where(Patient.id == patient_id)
            ).one()
        except NoResultFound as e:
            raise NotFoundError(
                f"No patient found with id {patient_id}"
            ) from e
        return result

    def delete(self, patient_id: str) -> None:
        """Delete a patient."""
        with self.Session.begin() as session:
            patient = self._read(patient_id, session)
            if patient is None:
                raise NotFoundError(f"No patient found with id {patient_id}")
            return self._delete(patient, session)

    def _delete(self, patient: Patient, session: Session) -> None:
        """Delete a patient."""
        session.delete(patient)

    def list(self) -> Sequence[Patient]:
        """List patients."""
        with self.Session.begin() as session:
            return self._list(session)

    def _list(self, session: Session) -> Sequence[Patient]:
        """List patients."""
        return [row[0] for row in session.execute(select(Patient)).fetchall()]


if __name__ == "__main__":
    dao = PatientDao("sqlite:///test.db")
    dao.create_table()
    patient = dao.create(date_of_birth=datetime.now())
    patient_id = patient.id
    assert patient_id is not None, "Something went wrong"

    print(dao.list())
    print(dao.read(patient_id))
    dao.delete(patient_id)
    # print(dao.read(patient_id))
