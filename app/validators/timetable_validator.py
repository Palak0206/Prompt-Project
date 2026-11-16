
from datetime import timedelta

from app.models.input_models import StudentInput
from app.models.output_models import TimetableOutput


def validate_timetable(
    timetable: TimetableOutput,
    student: StudentInput
) -> list[str]:

    errors = []

    # -----------------------------------
    # 1. Calculate expected planning dates
    # -----------------------------------

    start_date = student.start_date

    latest_exam_date = max(
        subject.exam_date for subject in student.subjects
    )

    expected_dates = []

    current_date = start_date

    while current_date <= latest_exam_date:
        expected_dates.append(current_date)
        current_date += timedelta(days=1)

    actual_dates = [
        day.date for day in timetable.days
    ]

    # -----------------------------------
    # 2. Check missing and duplicate dates
    # -----------------------------------

    if len(actual_dates) != len(set(actual_dates)):
        errors.append("Duplicate dates found in timetable.")

    if actual_dates != expected_dates:
        errors.append(
            "Timetable must contain every planning date "
            "exactly once and in chronological order."
        )

    # -----------------------------------
    # 3. Prepare subject information
    # -----------------------------------

    subject_map = {
        subject.name: subject
        for subject in student.subjects
    }

    daily_limit_minutes = int(
        student.max_daily_hours * 60
    )

    # -----------------------------------
    # 4. Validate every day's sessions
    # -----------------------------------

    for day in timetable.days:

        daily_study_minutes = 0

        for item in day.items:

            # Breaks do not count as study time
            if item.kind == "break":
                continue

            # Check whether the subject exists
            if item.subject not in subject_map:

                errors.append(
                    f"Unknown subject '{item.subject}' "
                    f"scheduled on {day.date}."
                )

                continue

            subject = subject_map[item.subject]

            # Check examination date
            if day.date >= subject.exam_date:

                errors.append(
                    f"{subject.name} is scheduled on or "
                    f"after its exam date ({day.date})."
                )

            # Check syllabus topics
            if subject.topics:

                allowed_topics = {
                    topic.casefold()
                    for topic in subject.topics
                }

                for topic in item.topics:

                    if topic.casefold() not in allowed_topics:

                        errors.append(
                            f"Invalid topic '{topic}' for "
                            f"{subject.name} on {day.date}."
                        )

            elif item.topics:

                errors.append(
                    f"Topics must be empty for {subject.name} "
                    "because no syllabus topics were supplied."
                )

            # Calculate study time
            daily_study_minutes += item.duration_minutes

        # -----------------------------------
        # 5. Check daily study-hour limit
        # -----------------------------------

        if daily_study_minutes > daily_limit_minutes:

            errors.append(
                f"Daily study limit exceeded on {day.date}: "
                f"{daily_study_minutes} minutes scheduled, "
                f"but only {daily_limit_minutes} minutes available."
            )

    return errors
