"""Lab data access."""
import uuid
from datetime import datetime
from typing import Sequence

from dao.models import Base, Lab
from sqlalchemy import (
    create_engine,
    select,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, sessionmaker


class LabDao:
    """Lab data access object."""

    def __init__(self, database_path: str) -> None:
        """Initialize."""
        self.engine = create_engine(
            database_path,
            isolation_level="SERIALIZABLE",
        )
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_table(self) -> None:
        """(Re-)create labs table."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

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
            raise ValueError(f"No lab found with id {lab_id}") from e
        return result

    def delete(self, lab_id: str) -> None:
        """Delete a lab."""
        with self.Session.begin() as session:
            lab = self._read(lab_id, session)
            if lab is None:
                raise ValueError(f"No lab found with id {lab_id}")
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


if __name__ == "__main__":
    dao = LabDao("sqlite:///test.db")
    dao.create_table()
    lab = dao.create(
        patient_id="Alice",
        admission_number=0,
        datetime=datetime.now(),
        name="a",
        value=1.0,
        units="m",
    )
    lab_id = lab.id
    assert lab_id is not None, "Something went wrong"

    print(dao.list())
    print(dao.read(lab_id))
    dao.delete(lab_id)
    # print(dao.read(lab_id))