Task 2: Input and Output Data Design
AI-Powered Timetable and Study Plan Generator
Data Modeling
API Contract Design
Pydantic Compatible

Objective: Finalize the JSON contracts between the frontend, Flask backend, prompt builder and LLM.

Scope: Input schema, output schema, validation responsibilities and edge cases.

No application code or timetable generation is included.

1. Data Design Principles
Before defining the schemas, we need to establish a few design decisions.

Your application has two distinct data models:
Input Data Model
Student → Backend
Contains the student's academic information and scheduling constraints.


Output Data Model
LLM → Backend → Student
Contains the AI-generated study sessions, activities and breaks.


The models should follow these principles:
Principle	Design decision
Simplicity	Only collect information necessary for planning
Consistency	Use predictable field names and data types
Extensibility	Allow additional fields in future versions
Validation	Define strict rules for important fields
Separation of responsibility	Python calculates objective values; LLM makes planning decisions
No redundant information	Avoid asking the LLM to return values Python can calculate

1.1 Important Date Decision
The planning period should be:
\[
\text{Planning Period} =
[\text{Start Date}, \text{Latest Exam Date})
\]

This means:
- The start date is included.
- The latest examination date is excluded from the overall planning period.
- Each subject's own examination date is excluded from its study sessions.
For example, if the last examination is on 25 November, the final study day is 24 November.

However, if another subject has its examination on 20 November, other subjects with later examinations can still receive sessions on 20 November.

This distinction is important for your validation logic.

2. Student Input Data Model
I recommend keeping the input JSON divided into three top-level sections:
1. plan
2. subjects
3. preferences
The first two are mandatory. Preferences are optional.
2.1 Input Schema Overview
Student Input
plan
- start_date
- available_hours_per_day

subjects[]
- name
- exam_date
- difficulty
- preparation_percentage
- topics (optional)

preferences (optional)

- preferred_session_duration_minutes


2.2 General Plan Fields
Field	Data type	Required	Validation
start_date	String (ISO date)	Yes	Valid date, YYYY-MM-DD
available_hours_per_day	Number	Yes	Greater than 0, maximum 24

Why use hours instead of minutes here?
The student naturally understands availability in hours.

For example, 4 hours per day is more intuitive than entering 240 minutes.

However, the backend should convert hours into minutes for calculations:
\[
\text{Available Minutes} =
\text{Available Hours} \times 60
\]

I recommend allowing fractional hours, such as 2.5 hours.

Additional validation: Require available hours to have at most two decimal places, so conversions to minutes remain precise.
2.3 Subject Fields
Each subject should have the following structure.
Field	Data type	Required	Allowed values / rules
name	String	Yes	Non-empty, trimmed
exam_date	String	Yes	Valid ISO date
difficulty	String	Yes	Easy, Medium, Hard
preparation_percentage	Integer	Yes	0–100
topics	Array of strings	No	Non-empty topic names

Why is topics optional?
Because not every student knows their complete syllabus when creating a timetable.

If topics are provided, the LLM should use them when constructing tasks.

If they are missing, the LLM can create generic tasks such as:
- Review difficult concepts.
- Practice numerical questions.
- Revise previously studied material.
It must not invent textbook chapters or claim that a specific chapter belongs to the student's syllabus.
Subject naming
Subject names should be unique after trimming whitespace and applying case-insensitive comparison.

For example:
- Mathematics
- mathematics
These should be treated as the same subject.

This prevents ambiguity when the LLM references subjects in its output.
2.4 Preferences
For the MVP, I recommend only one optional preference:
Field	Data type	Required	Default
preferred_session_duration_minutes	Integer	No	60

Suggested range: 25–120 minutes.

Why include it?

Students may prefer shorter or longer uninterrupted study sessions.

It influences how the LLM divides study activities without introducing complicated scheduling requirements.

I would exclude preferred study time, sleep schedule, daily availability windows and numerous personal preferences because you have explicitly decided not to collect clock-time availability.

2.5 Representative Input JSON
The following is the recommended input contract.

{
  "plan": {
    "start_date": "2026-11-16",
    "available_hours_per_day": 4,
    "unavailable_dates": []
  },
  "subjects": [
    {
      "name": "Mathematics",
      "exam_date": "2026-11-20",
      "difficulty": "Hard",
      "preparation_percentage": 40,
      "topics": [
        "Integration",
        "Differential Equations",
        "Matrices"
      ]
    },
    {
      "name": "DBMS",
      "exam_date": "2026-11-22",
      "difficulty": "Medium",
      "preparation_percentage": 60,
      "topics": [
        "SQL",
        "Normalization",
        "Transactions"
      ]
    },
    {
      "name": "Operating Systems",
      "exam_date": "2026-11-25",
      "difficulty": "Hard",
      "preparation_percentage": 30,
      "topics": []
    }
  ],
  "preferences": {
    "preferred_session_duration_minutes": 60
  }
}



I have included unavailable_dates as an optional field under plan.

This is a small but useful addition. It allows a student to indicate that they cannot study on particular dates without introducing exact clock-time availability.

If omitted, the backend should assume that every date is potentially available.

An empty array means there are no specifically blocked dates.
2.6 Input Validation Rules
I recommend implementing these rules before calling the LLM.
ID	Validation rule	Action if invalid
IN-01	plan must exist	Reject request
IN-02	subjects must contain at least one subject	Reject request
IN-03	Subject names must be unique	Reject request
IN-04	Difficulty must be Easy, Medium or Hard	Reject request
IN-05	Preparation must be an integer from 0–100	Reject request
IN-06	Exam dates must be valid dates	Reject request
IN-07	Exam dates cannot precede the start date	Reject request
IN-08	At least one study day must exist before the latest examination	Reject request
IN-09	Available hours must be greater than zero and at most 24	Reject request
IN-10	Topics must be valid strings if provided	Reject request
IN-11	Unavailable dates must fall within the planning period	Reject request
IN-12	Preferred session duration must be within the permitted range	Reject request

One subtle distinction: missing versus empty topics
These two inputs should have the same practical meaning:
- topics omitted.
- "topics": []
Both indicate that the student has not supplied syllabus topics.

However, null should not be accepted as a topic list. It is better to have a predictable array type.

3. LLM Output Data Model
Now we need to design the structure returned by the LLM.

The output schema is slightly more important than the input schema because the backend must process it without making assumptions about how the LLM formats its response.
3.1 Output Design Decisions
I recommend the following:
1. Use one top-level timetable object.
2. Store all dates in a days array.
3. Store daily activities in an ordered items array.
4. Represent study sessions and breaks as different item types.
5. Store durations in integer minutes.
6. Do not include daily totals or weekday names.
7. Do not include clock times.
Why an ordered items array?
Initially, you might consider keeping two separate arrays:
- sessions
- breaks
However, this creates a problem.

How would the frontend know whether a break occurs between the first and second study sessions or after all sessions?

An ordered array solves this problem.

Each item can represent either a study session or a break.
Example of the daily activity sequence
Study
Mathematics

Learning · 60 minutes

Break
Rest

15 minutes

Study
DBMS

Practice · 45 minutes

Illustrative sequence showing how study sessions and breaks coexist in one ordered list.
This also makes frontend rendering much easier.
3.2 Output Schema Overview
Field	Data type	Required	Description
timetable	Object	Yes	Main output
start_date	String	Yes	Planning start date
end_date_exclusive	String	Yes	First date outside planning period
days	Array	Yes	Every date in the planning period
date	String	Yes	Individual study date
items	Array	Yes	Ordered daily activities
type	String	Yes	study_session or break
subject	String	For study	Submitted subject name
task	String	For study	Specific study activity
session_type	String	For study	Activity category
duration_minutes	Integer	Yes	Duration of the item

3.3 Study Session Types
I recommend exactly four session types for the MVP.
Value	Purpose
learning	Understanding new or incomplete concepts
practice	Solving problems and questions
revision	Reviewing previously studied material
mock_test	Simulating examination conditions

Why not introduce more?

You could add assignment, research, video_learning, note_making, etc.

But those activities can be described within the task field.

Four categories are enough to organize and analyze the schedule.
3.4 Break Representation
Breaks should have their own item type.

A break should contain:
- type
- duration_minutes
It should not contain a subject or study task.

This ensures that Python can distinguish study time from resting time.

For example:
- Study session: 60 minutes.
- Break: 15 minutes.
- Study session: 45 minutes.
Total study time = 105 minutes, not 120 minutes.
3.5 Representative Output JSON
The following is a fictional structural example using two subjects.

It deliberately shows only a small number of activities to illustrate the contract.

{
  "timetable": {
    "start_date": "2026-06-01",
    "end_date_exclusive": "2026-06-03",
    "days": [
      {
        "date": "2026-06-01",
        "items": [
          {
            "type": "study_session",
            "subject": "Biology",
            "task": "Review supplied cell biology topics",
            "session_type": "revision",
            "duration_minutes": 60
          },
          {
            "type": "break",
            "duration_minutes": 15
          },
          {
            "type": "study_session",
            "subject": "History",
            "task": "Practice questions on supplied topics",
            "session_type": "practice",
            "duration_minutes": 45
          }
        ]
      },
      {
        "date": "2026-06-02",
        "items": [
          {
            "type": "study_session",
            "subject": "History",
            "task": "Revise important concepts",
            "session_type": "revision",
            "duration_minutes": 60
          }
        ]
      }
    ]
  }
}



Assume Biology has an examination on 2 June and History has an examination on 3 June.

Notice that:
- Biology receives no study session on its examination date.
- History can still be studied on 2 June.
- The output contains both dates in the planning period.
- Break duration is separate from study duration.
- No clock times are required.
- No daily totals are returned.
3.6 Output Validation Rules
ID	Validation rule	Severity
OUT-01	Root must contain timetable	Hard
OUT-02	Required timetable fields must exist	Hard
OUT-03	Every planning date must be present	Hard
OUT-04	Dates must be in chronological order	Hard
OUT-05	No duplicate dates	Hard
OUT-06	Item type must be valid	Hard
OUT-07	Study session must reference a submitted subject	Hard
OUT-08	Study session must have a task	Hard
OUT-09	Session type must belong to the permitted enum	Hard
OUT-10	Durations must be positive integers	Hard
OUT-11	Subject examination date must be later than session date	Hard
OUT-12	Daily study duration must not exceed available hours	Hard
OUT-13	Break duration must not count towards study hours	Hard
OUT-14	No study sessions on unavailable dates	Hard
OUT-15	Breaks should be sensibly positioned	Soft, unless they overlap a session in a time-based extension

One important addition: unexpected fields
I recommend rejecting unexpected fields in the LLM output rather than silently accepting them.

For example, if the model returns:

"start_time": "09:00"

that field is not part of the agreed output contract.

Rejecting unexpected fields helps detect when the model drifts away from the intended schema.

Pydantic can enforce this using strict model configuration.

4. Validation Strategy: Who Is Responsible for What?
This distinction should be finalized before implementation.

There are three separate responsibilities.
4.1 Python Input Validation
Before API call
Python checks whether the student's information is valid.

Examples:
- Are all mandatory fields present?
- Is the preparation percentage between 0 and 100?
- Are examination dates valid?
- Is there at least one subject?
- Are subject names unique?
- Are preferences within permitted ranges?
Python should also calculate:
- Latest examination date.
- Planning period.
- Available daily minutes.
- Subject-specific preparation remaining.
These values can then be supplied to the prompt builder as derived context.
4.2 LLM Responsibilities
Planning decisions
The LLM should decide:
- Which subject deserves more attention.
- Which activities should be scheduled.
- Which topics should be prioritized.
- How learning and practice should be sequenced.
- When revision should occur.
- Whether mock tests are appropriate.
- How to distribute the available time.
The LLM should also produce a short, sensible explanation of its planning decisions only if you later choose to add a separate explanation field.

For the current MVP, I recommend keeping explanations out of the JSON output. They can be generated separately later.
4.3 Python Output Validation
After API call
Python must independently verify every objective constraint.

The following distinction is especially important:
Rule	LLM	Python
Prioritize difficult subjects	Decide	No need to dictate exact priority
Choose study tasks	Decide	Check task is non-empty
Select session type	Decide	Verify permitted value
Respect examination dates	Instruct	Enforce
Respect daily study limit	Instruct	Enforce
Include every planning date	Instruct	Enforce
Use supplied subjects only	Instruct	Enforce
Calculate daily study total	Not required	Calculate
Include appropriate revision	Decide	Check coverage
Avoid invented syllabus chapters	Instruct	Check against supplied topics where possible

Important: Python can verify whether revision sessions exist, but it cannot objectively determine whether the revision allocation is pedagogically sufficient. That remains a planning-quality decision.

5. Hard Constraints vs Soft Preferences
This separation will prevent your validation system from becoming unnecessarily restrictive.
Category	Rule	Enforcement
Hard	No study after a subject's exam date	Python
Hard	No study on unavailable dates	Python
Hard	Daily study time within maximum	Python
Hard	Valid session durations	Python
Hard	Only submitted subjects	Python
Hard	All planning dates represented	Python
Hard	Valid JSON structure	Python
Soft	Difficult subjects should receive more attention	LLM
Soft	Less-prepared subjects should receive more attention	LLM
Soft	Revision before examinations	LLM
Soft	Balanced study sessions	LLM
Soft	Breaks between long sessions	LLM
Soft	Avoid excessive repetition	LLM

One nuance: breaks are optional as a planning decision, but if a break is included, its duration and placement must be structurally valid.

Similarly, a subject with 100% preparation may still need revision. The application should not automatically force it to receive zero study time.

6. Edge Cases and Recommended Handling
This is where your data model needs to be particularly robust. A technically valid JSON response does not necessarily represent a valid timetable.

Here are the important scenarios.
6.1 Two Subjects Have the Same Examination Date
Example:
- Mathematics: 20 November.
- DBMS: 20 November.
- Operating Systems: 25 November.
Expected behavior:
- Both Mathematics and DBMS can be studied until 19 November.
- Neither can receive a study session on 20 November.
- Operating Systems can still receive study sessions on 20 November.
Validation: Compare every session date against the examination date of the particular subject, not against the earliest examination date globally.
Accept input
6.2 Examination Date Equals Plan Start Date
Example:
- Start date: 16 November.
- Mathematics examination: 16 November.
- DBMS examination: 20 November.
Expected behavior:
- Mathematics receives no preparation sessions.
- DBMS can be scheduled normally from 16 November onward.
- The Mathematics examination date should not invalidate the entire request.
If every subject has an examination on the start date, the planning period contains no study days.

Recommendation: Reject that request with a clear message explaining that no preparation days are available.
Conditional acceptance
6.3 Student Has Very Few Available Hours
Example: 30 minutes per day.

The application should:
- Accept the input if it is a valid positive duration.
- Avoid forcing the timetable to fill all available time.
- Allow short study sessions.
- Prioritize the most urgent preparation.
- Avoid generating unrealistic allocations.
I recommend accepting availability down to 15 minutes per day (0.25 hours) in the MVP.

Anything below that is unlikely to produce a meaningful study session.
Accept input
6.4 Subject Has 100% Preparation
A fully prepared subject does not necessarily require zero study time.

The LLM can schedule:
- Short revision sessions.
- Formula reviews.
- Mock tests.
- Practice of difficult questions.
Recommendation: Do not force a minimum study allocation for subjects with 100% preparation. Allow the LLM to decide whether revision is worthwhile.
Accept input
6.5 Subject Has 0% Preparation
The subject requires significant attention.

The LLM should prioritize:
- Learning fundamental concepts.
- Covering supplied topics.
- Basic practice.
- Revision of completed material as the examination approaches.
If the syllabus is not supplied, the LLM should use general learning tasks rather than inventing chapter names.
Accept input
6.6 No Syllabus Topics Supplied
This is a perfectly valid scenario.

For example:
{
  "name": "Mathematics",
  "exam_date": "2026-11-20",
  "difficulty": "Hard",
  "preparation_percentage": 40,
  "topics": []
}


The LLM can generate generic tasks such as:
- Review incomplete concepts.
- Practice numerical questions.
- Revise difficult areas.
It must not fabricate the student's actual syllabus.
Accept input
6.7 Planning Period Contains Days With No Available Study Time
This is why I recommended adding unavailable_dates to the input schema.

For example:
{
  "unavailable_dates": [
    "2026-11-18",
    "2026-11-21"
  ]
}


Expected behavior:
- Those dates must still appear in the output.
- Their items arrays must be empty.
- No study sessions or breaks should be scheduled on those dates.
An empty date entry is valid. It represents an intentionally free day, not missing AI output.
Accept input
6.8 LLM Returns Missing or Invalid Fields
Examples:
- Missing duration_minutes.
- Invalid session type such as watching_video.
- Missing subject.
- String instead of integer duration.
- Invalid date format.
- Missing items array.
Expected behavior:
1. Parse the JSON.
2. Validate it against the output schema.
3. Collect validation errors.
4. Request correction from the LLM.
5. Validate again.
6. Stop after the retry limit.
Do not display partially valid timetables.
Regeneration required
6.9 LLM Exceeds the Daily Study-Hour Limit
Suppose the student has a maximum of 4 hours, but the LLM generates 5 hours of study sessions.

Python should calculate the total independently.
\[
\text{Daily Study Minutes}
=
\sum \text{Study Session Durations}
\]

If:
\[
\text{Daily Study Minutes} > 240
\]

the response is invalid.

Expected behavior: Reject the timetable and request regeneration with the exact violation.

Do not silently reduce individual session durations because that may change the intended study plan.
Reject generated response
6.10 Additional Edge Cases Worth Handling
Scenario	Recommended behavior
Duplicate subject names	Reject input
Exam dates in reverse order	Accept; subjects can have any exam order
One subject has no available preparation days	Warn the student; do not invent study dates
All subjects have 100% preparation	Allow revision-focused planning
All subjects have 0% preparation	Allow the LLM to prioritize foundational learning
LLM returns an unknown subject	Reject output
LLM returns zero or negative duration	Reject output
LLM returns a missing date	Reject output
LLM returns an extra field	Reject output
LLM returns a day with no activities	Accept if the date is legitimately free or the planner chooses a rest day


7. Recommended Pydantic Modeling Approach
Since you're planning to use Flask and Pydantic, there are a few modeling decisions worth finalizing.

You don't need to implement anything yet, but these are the model types I recommend.
7.1 Input Models
Pydantic model	Responsibility
PlanInput	Start date, daily hours and unavailable dates
SubjectInput	Subject-specific academic information
PreferencesInput	Optional study preferences
StudentInput	Combines the three input models

7.2 Output Models
Pydantic model	Responsibility
StudySession	Study task and duration
BreakSession	Break duration
DaySchedule	Date and ordered activities
TimetableOutput	Complete timetable

Important: Use a discriminated union
Your items array contains two different object types:
- Study session.
- Break.
A discriminated union allows Pydantic to identify which structure to validate based on the type field.

For example:
- If type = study_session, require subject, task and session type.
- If type = break, require only duration.
This is cleaner than creating one large model containing many optional fields.
Additional Pydantic recommendations
- Use date for internal date validation.
- Use Literal or enums for fixed values.
- Use Field constraints for numeric ranges.
- Configure models to reject unexpected fields.
- Use model-level validators for relationships between fields.
- Keep scheduling validation separate from basic schema validation.
One distinction: Pydantic checks data structure and field-level rules. Your custom Python validation service should handle cross-field scheduling rules, such as daily study-hour totals and examination deadlines.

8. Final Schema Recommendations
After considering the edge cases, I recommend one small refinement to the output design.

Earlier, I included start_date and end_date_exclusive in the LLM response. However, both values are already known from the student's input.

The LLM should not return redundant information that Python can calculate reliably.

Therefore, the final output contract should contain only the days array inside timetable.

Python already knows the expected date range and can verify that every date is present.
8.1 Final Recommended Input Structure
Recommended for implementation
{
  "plan": {
    "start_date": "2026-11-16",
    "available_hours_per_day": 4,
    "unavailable_dates": []
  },
  "subjects": [
    {
      "name": "Mathematics",
      "exam_date": "2026-11-20",
      "difficulty": "Hard",
      "preparation_percentage": 40,
      "topics": ["Integration", "Matrices"]
    },
    {
      "name": "DBMS",
      "exam_date": "2026-11-22",
      "difficulty": "Medium",
      "preparation_percentage": 60,
      "topics": ["SQL", "Normalization"]
    }
  ],
  "preferences": {
    "preferred_session_duration_minutes": 60
  }
}


8.2 Final Recommended Output Structure
Recommended for implementation
{
  "timetable": {
    "days": [
      {
        "date": "2026-11-16",
        "items": [
          {
            "type": "study_session",
            "subject": "Mathematics",
            "task": "Practice integration problems",
            "session_type": "practice",
            "duration_minutes": 60
          },
          {
            "type": "break",
            "duration_minutes": 15
          }
        ]
      },
      {
        "date": "2026-11-17",
        "items": []
      }
    ]
  }
}


This is a partial structural illustration, not a complete timetable.
8.3 Fields to Exclude from the MVP
I recommend deliberately excluding the following:
Field	Reason for exclusion
Student name	Not necessary for generation
Student age	Does not materially improve scheduling
College name	Not required
Exact study start/end times	Student does not provide clock-time availability
Weekday names	Python can calculate them
Daily total study minutes	Python can calculate them
Total break minutes	Python can calculate them
Overall preparation score	Not needed for the initial generation
Subject priority score	Can be introduced as a future enhancement
Timetable explanation	Can be generated separately later
Completion tracking	Requires additional functionality
Multiple preference fields	Unnecessary complexity for MVP


9. Unresolved Decisions Before Implementation
There are a few decisions I would finalize before moving to application code.
Proposed design decisions

These are my recommended defaults. You can change them before implementation.
1. Daily study availability

Should unavailable_dates be sufficient, with all other dates assumed available up to the daily maximum?
Use unavailable_dates
Recommended




2. Session duration preference

Should the preferred duration be a strict limit or simply a preference?
Soft preference; allow deviations
Recommended




3. Break duration

Should break duration be decided by the LLM or fixed by the application?
LLM decides within reasonable bounds
Recommended




4. Empty study days

Should the LLM be allowed to leave a day empty even when it is available?
Yes, allow rest days
Recommended




5. Strict output schema

Should unexpected LLM fields be rejected?
Yes, reject unexpected fields
Recommended




6. Regeneration limit

How many attempts should the backend make after invalid output?
Maximum 2 retries
Recommended




My recommendations are to keep all six defaults as proposed.

10. Final Deliverables for Task 2
Here is what we have finalized conceptually:
Deliverable	Status
Student input JSON structure	Defined
Subject data structure	Defined
Optional preferences	Defined
Timetable output structure	Defined
Study session types	Defined
Break representation	Defined
Input validation rules	Defined
Output validation rules	Defined
Edge-case handling	Defined
Pydantic model boundaries	Defined

What comes next?
I recommend moving to Task 3: Data Models and Input Validation.

The next implementation milestone should be:
1. Create the Pydantic input models.
2. Create the Pydantic output models.
3. Implement input validation.
4. Implement the basic timetable output validator.
5. Write Pytest test cases for valid and invalid data.
Only after these contracts work should we start building the dynamic prompt engine.

One architectural principle to carry forward: The JSON schemas are contracts between components. The frontend, Flask backend, prompt builder and LLM must all agree on these contracts. If you change a field later, update the relevant models and tests together. This will save you a lot of debugging when the application becomes more complex.