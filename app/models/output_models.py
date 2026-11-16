
from datetime import date
from typing import Literal, Annotated

from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


# -----------------------------------------
# 1. Study Session Model
# -----------------------------------------

class StudySession(BaseModel):

    model_config = ConfigDict(extra="forbid")

    kind: Literal["session"]

    subject: str = Field(min_length=1)

    session_type: Literal[
        "learning",
        "practice",
        "revision",
        "mock_test"
    ]

    task: str = Field(min_length=1, max_length=200)

    topics: list[str] = Field(default_factory=list)

    duration_minutes: int = Field(gt=0)


# -----------------------------------------
# 2. Break Session Model
# -----------------------------------------

class BreakSession(BaseModel):

    model_config = ConfigDict(extra="forbid")

    kind: Literal["break"]

    duration_minutes: int = Field(gt=0)


# -----------------------------------------
# 3. Discriminated Union
# -----------------------------------------

ScheduleItem = Annotated[
    StudySession | BreakSession,
    Field(discriminator="kind")
]


# -----------------------------------------
# 4. Day Schedule Model
# -----------------------------------------

class DaySchedule(BaseModel):

    model_config = ConfigDict(extra="forbid")

    date: date

    items: list[ScheduleItem] = Field(
        default_factory=list
    )


# -----------------------------------------
# 5. Complete Timetable Model
# -----------------------------------------

class TimetableOutput(BaseModel):

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]

    days: list[DaySchedule] = Field(min_length=1)

