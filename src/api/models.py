"""Pydantic models for HTTP API."""

import datetime
import enum
from typing import Optional

from pydantic import BaseModel

from dao.models import (
    Gender as StorageGender,
)
from dao.models import (
    Lab as StorageLab,
)
from dao.models import (
    Language as StorageLanguage,
)
from dao.models import (
    MaritalStatus as StorageMaritalStatus,
)
from dao.models import (
    Patient as StoragePatient,
)
from dao.models import (
    Race as StorageRace,
)


class Gender(enum.StrEnum):
    """Gender."""

    unknown = "unknown"
    male = "male"
    female = "female"
    other = "other"

    @staticmethod
    def from_storage(value: StorageGender) -> "Gender":
        """Convert a storage Gender to an API Gender."""
        return Gender[value.name]


class MaritalStatus(enum.StrEnum):
    """Marital status."""

    unknown = "unknown"
    single = "single"
    married = "married"
    separated = "separated"
    divorced = "divorced"

    @staticmethod
    def from_storage(value: StorageMaritalStatus) -> "MaritalStatus":
        """Convert a storage MaritalStatus to an API MaritalStatus."""
        return MaritalStatus[value.name]


class Race(enum.StrEnum):
    """Race."""

    unknown = "unknown"
    white = "White"
    african_american = "African American"
    asian = "Asian"

    @staticmethod
    def from_storage(value: StorageRace) -> "Race":
        """Convert a storage Race to an API Race."""
        return Race[value.name]


class Language(enum.StrEnum):
    """Language."""

    unknown = "unknown"
    english = "English"
    spanish = "Spanish"
    icelandic = "Icelandic"

    @staticmethod
    def from_storage(value: StorageLanguage) -> "Language":
        """Convert a storage Language to an API Language."""
        return Language[value.name]


class InputPatient(BaseModel):
    """Patient."""

    gender: Gender
    date_of_birth: datetime.datetime
    language: Language
    marital_status: MaritalStatus
    race: Race


class Patient(InputPatient):
    """Patient."""

    id: Optional[str]  # output-only

    @staticmethod
    def from_storage(patient: StoragePatient) -> "Patient":
        """Convert a storage Patient to an API Patient."""
        return Patient(
            id=patient.id,
            gender=Gender.from_storage(patient.gender),
            date_of_birth=patient.date_of_birth,
            language=Language.from_storage(patient.language),
            marital_status=MaritalStatus.from_storage(patient.marital_status),
            race=Race.from_storage(patient.race),
        )


class InputLab(BaseModel):
    """Lab measurement."""

    admission_number: int
    datetime: datetime.datetime
    name: str
    value: float
    units: str


class Lab(InputLab):
    """Lab measurement."""

    id: Optional[str]
    patient_id: Optional[str]

    @staticmethod
    def from_storage(lab: StorageLab) -> "Lab":
        """Convert a storage Lab to an API Lab."""
        return Lab(
            id=lab.id,
            patient_id=lab.patient_id,
            admission_number=lab.admission_number,
            datetime=lab.datetime,
            name=lab.name,
            value=lab.value,
            units=lab.units,
        )
