
from decimal import Decimal
from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator
)


# ------------------------------------------------
# 1. Subject Input Model
# ------------------------------------------------

class SubjectInput(BaseModel):

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=60)

    exam_date: date

    difficulty: Literal["easy", "medium", "hard"]

    preparation_percentage: int = Field(ge=0, le=100)

    topics: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def clean_subject_name(cls, value):
        value = " ".join(value.split())

        if not value:
            raise ValueError("Subject name cannot be empty")

        return value

    @field_validator("topics")
    @classmethod
    def clean_topics(cls, topics):
        cleaned_topics = []

        for topic in topics:
            topic = " ".join(topic.split())

            if not topic:
                raise ValueError("Topic names cannot be empty")

            cleaned_topics.append(topic)

        return cleaned_topics


# ------------------------------------------------
# 2. Preferences Input Model
# ------------------------------------------------

class PreferencesInput(BaseModel):

    model_config = ConfigDict(extra="forbid")

    max_session_duration_minutes: int = Field(
        default=90,
        ge=15,
        le=180
    )


# ------------------------------------------------
# 3. Main Student Input Model
# ------------------------------------------------

class StudentInput(BaseModel):

    model_config = ConfigDict(extra="forbid")

    start_date: date

    max_daily_hours: Decimal = Field(
        gt=0,
        le=24
    )

    subjects: list[SubjectInput] = Field(min_length=1)

    preferences: PreferencesInput = Field(
        default_factory=PreferencesInput
    )

    @field_validator("max_daily_hours")
    @classmethod
    def validate_daily_hours(cls, value):

        minutes = value * 60

        if minutes % 15 != 0:
            raise ValueError(
                "Daily study hours must be in 15-minute increments"
            )

        return value

    @model_validator(mode="after")
    def validate_subjects_and_dates(self):

        # Check for duplicate subject names
        subject_names = [
            subject.name.casefold()
            for subject in self.subjects
        ]

        if len(subject_names) != len(set(subject_names)):
            raise ValueError("Subject names must be unique")

        # Every exam must be on or after the start date
        for subject in self.subjects:

            if subject.exam_date < self.start_date:
                raise ValueError(
                    f"Exam date for {subject.name} "
                    "cannot be before the plan start date"
                )

        # At least one study day must exist
        if all(
            subject.exam_date == self.start_date
            for subject in self.subjects
        ):
            raise ValueError(
                "No preparation days available. "
                "All exams are on the plan start date."
            )

        return self
