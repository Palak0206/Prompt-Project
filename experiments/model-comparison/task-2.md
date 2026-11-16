# Task 2 — Input and Output Data Schema Comparison

## Objective

Compare two independently generated data designs for the AI-powered Timetable and Study Plan Generator.

## 1. Comparison

| Area | ChatGPT | Claude | Decision |
|---|---|---|---|
| Input structure | Nested plan object | Flat structure | Use simpler flat structure |
| Subject fields | Name, exam date, difficulty, preparation percentage, topics | Similar fields | Adopt |
| Preferences | Session duration and unavailable dates | Maximum session duration | Keep session duration only |
| Output structure | Ordered items array | Ordered items array | Adopt |
| Break representation | Separate item type | Discriminated item type | Adopt Claude's `kind` |
| Session categories | Four types | Four types | Adopt |
| Validation | Pydantic and Python checks | Detailed structural and scheduling checks | Adopt Claude's approach |
| Schema version | Not included | Included | Adopt |
| Revision requirement | Recommended | Mandatory | Keep as a soft recommendation |

## 2. Final Input Design

Top-level fields:
- `start_date`
- `max_daily_hours`
- `subjects`
- `preferences`

Each subject:
- `name`
- `exam_date`
- `difficulty`
- `preparation_percentage`
- `topics`

Optional preference:
- `max_session_duration_minutes`, default 90.

Unavailable dates are excluded from the MVP.

## 3. Final Output Design

Top-level fields:
- `schema_version`
- `days`

Each day:
- `date`
- `items`

Each item is either:
- A study session (`kind: session`)
- A break (`kind: break`)

Study sessions contain:
- `subject`
- `session_type`
- `task`
- `topics`
- `duration_minutes`

Breaks contain:
- `duration_minutes`

Session types:
- `learning`
- `practice`
- `revision`
- `mock_test`

## 4. Important Design Decisions

1. The planning period includes the start date and latest exam date.
2. A subject cannot receive a study session on or after its exam date.
3. Other subjects can still be scheduled on another subject's exam date.
4. Empty days are permitted.
5. Revision is encouraged but not a mandatory hard constraint.
6. Python calculates daily totals and other derived information.
7. Python independently validates all hard scheduling constraints.
8. Invalid LLM output can be regenerated a limited number of times.
9. Syllabus topics must not be fabricated.
10. No clock times, student personal information, or complex preferences are required in the MVP.

## 5. Final Verdict

Claude provided the more detailed technical validation strategy. ChatGPT contributed a clear and useful data organization approach.

The final design combines the useful ideas from both while removing unnecessary complexity.

## 6. Next Task

Phase 1, Task 3: Implement the initial application data models and input validation using Python, Pydantic, and Pytest.