"""Lab data access."""
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
from dao.models import Lab


class LabDao:
    """Lab data access object."""

    def __init__(self, engine: Engine) -> None:
        """Initialize."""
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create(
        self,
        patient_id: str,
        admission_number: int,
        datetime: datetime,
        name: str,
        value: float,
        units: str,
    ) -> Lab:
        """Create a lab."""
        with self.Session.begin() as session:
            return self._create(
                patient_id,
                admission_number,
                datetime,
                name,
                value,
                units,
                session,
            )

    def _create(
        self,
        patient_id: str,
        admission_number: int,
        datetime: datetime,
        name: str,
        value: float,
        units: str,
        session: Session,
    ) -> Lab:
        """Create a lab."""
        id = str(uuid.uuid4())
        lab = Lab(
            id=id,
            patient_id=patient_id,
            admission_number=admission_number,
            datetime=datetime,
            name=name,
            value=value,
            units=units,
        )
        session.add(lab)
        session.commit()
        return lab

    def read(self, lab_id: str) -> Lab:
        """Get a lab."""
        with self.Session.begin() as session:
            return self._read(lab_id, session)

    def _read(self, lab_id: str, session: Session) -> Lab:
        """Get a lab in a session."""
        try:
            result = session.scalars(select(Lab).where(Lab.id == lab_id)).one()
        except NoResultFound as e:
            raise NotFoundError(f"No lab found with id {lab_id}") from e
        return result

    def delete(self, lab_id: str) -> None:
        """Delete a lab."""
        with self.Session.begin() as session:
            lab = self._read(lab_id, session)
            if lab is None:
                raise NotFoundError(f"No lab found with id {lab_id}")
            return self._delete(lab, session)

    def _delete(self, lab: Lab, session: Session) -> None:
        """Delete a lab."""
        session.delete(lab)

    def list(self) -> Sequence[Lab]:
        """List labs."""
        with self.Session.begin() as session:
            return self._list(session)

    def _list(self, session: Session) -> Sequence[Lab]:
        """List labs."""
        return [row[0] for row in session.execute(select(Lab)).fetchall()]
