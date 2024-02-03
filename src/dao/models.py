"""Patient model for storage."""
import enum
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    create_engine,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    registry,
    relationship,
    sessionmaker,
)

mapper_registry: registry = registry()


class Gender(enum.StrEnum):
    """Gender."""

    unknown = "unknown"
    male = "male"
    female = "female"
    other = "other"


class MaritalStatus(enum.StrEnum):
    """Marital status."""

    unknown = "unknown"
    single = "single"
    married = "married"
    separated = "separated"
    divorced = "divorced"


class Race(enum.StrEnum):
    """Race."""

    unknown = "unknown"
    white = "White"
    african_american = "African American"
    asian = "Asian"


class Language(enum.StrEnum):
    """Language."""

    unknown = "unknown"
    english = "English"
    spanish = "Spanish"
    icelandic = "Icelandic"


class Base(DeclarativeBase):
    """Base class for models."""


class Patient(Base):
    """Patient."""

    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(primary_key=True)
    gender: Mapped[Gender]
    date_of_birth: Mapped[datetime]
    language: Mapped[Language]
    marital_status: Mapped[MaritalStatus]
    race: Mapped[Race]

    labs: Mapped[list["Lab"]] = relationship(back_populates="patient")


class Lab(Base):
    """Lab."""

    __tablename__ = "labs"

    id: Mapped[str] = mapped_column(primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    admission_number: Mapped[int]
    datetime: Mapped[datetime]
    name: Mapped[str]
    value: Mapped[float]
    units: Mapped[str]

    patient: Mapped["Patient"] = relationship(back_populates="labs")


if __name__ == "__main__":
    engine = create_engine("sqlite:///test.db")
    Session = sessionmaker(bind=engine)

    # create tables
    mapper_registry.metadata.drop_all(engine)
    mapper_registry.metadata.create_all(engine)

    # add patient
    patient = Patient(date_of_birth=datetime.now())
    session = Session()
    session.add(patient)
    print(patient)

    # fetch patients
    result = session.execute(select(Patient))
    print(result.fetchall())
