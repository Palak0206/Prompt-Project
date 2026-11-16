# Task 2: Input and Output Data Design

## 0. Changes from the Earlier Specification

This design narrows the earlier specification to match your new MVP constraints.

| Earlier spec | Task 2 decision | Reason |
|---|---|---|
| Days off, per-date hour overrides, max session length, break style, free-text note | **All removed** | Minimal preferences, no clock-time availability, no free text (removes the prompt-injection surface) |
| Off days (`is_off_day`) | **Removed**; every date is represented, empty `sessions` allowed | Simpler, and Python can derive "no study" from an empty list |
| `subject_allocation` in LLM output | **Removed** | Python can compute actual totals; planned values from the LLM would be redundant and untrustworthy |
| Exam-day `light_review` allowed on the exam date | **Replaced** by rule 1: no session for a subject on or after its exam date | Your rule 1 is stricter and simpler |
| Breaks tied to `after_session_order` in a separate list | **Breaks become session-list items** (`kind: break`) | One ordered list is easier to render and validate |

**Consequence of rule 1:** a subject's last study date is the day before its exam. The schema therefore has no `light_review` type, and the "revision on the day before" pattern is the final revision opportunity.

---

## A. Student Input Schema

### A.1 Top-level fields

| Field | Type | Required | Rules |
|---|---|---|---|
| `start_date` | string, ISO `YYYY-MM-DD` | Yes | Valid calendar date. Must not be after the earliest exam date (equal is a hard error, see edge cases). Must not be more than 1 day in the past (tolerance for time zones). |
| `max_daily_hours` | number | Yes | Range 0.5 to 16, in steps of 0.5. Stored as a limit, not a target. |
| `subjects` | array of Subject | Yes | 1 to 8 items. |
| `preferences` | object | Optional | See A.3. If omitted, defaults apply. |

### A.2 Subject object

| Field | Type | Required | Rules |
|---|---|---|---|
| `name` | string | Yes | Trimmed, 1 to 60 characters, no control characters, unique case-insensitively after trimming and collapsing whitespace. |
| `exam_date` | string, ISO date | Yes | Valid date, strictly after `start_date` (see edge cases for "same day"). Must not be more than ~120 days after `start_date` (keeps output within token limits). |
| `difficulty` | enum | Yes | `easy`, `medium`, `hard` (lowercase). The form may display capitalised labels, but the API accepts only the lowercase values. |
| `preparation_percent` | integer | Yes | 0 to 100 inclusive. Reject floats and numeric strings at the API boundary (or coerce deliberately, see unresolved decisions). |
| `topics` | array of string | Optional, default `[]` | Max 30 topics, each 1 to 80 characters, unique case-insensitively, empty strings dropped. |

### A.3 Preferences: which are genuinely necessary?

I evaluated each candidate:

| Candidate | Verdict | Justification |
|---|---|---|
| Days off | **Exclude** | This is a real need, but it implies per-day capacity and complicates every validator rule. Students can approximate it by reducing the daily limit. Strong candidate for v1.1. |
| Max session length | **Include (optional)** | Cheap, objectively checkable, and directly shapes the output. |
| Break preference | **Exclude** | Fixed Python-enforced defaults are enough (see section B.4). A setting adds testing cost for little value. |
| Revision preference (more/less) | **Exclude** | The budget logic already handles it, and the effect is not objectively verifiable. |
| Time-of-day preference | **Exclude** | You decided against clock times. |
| Free-text note | **Exclude** | Unverifiable, and an injection risk. |

**Recommended `preferences` object (one optional field):**

| Field | Type | Required | Rules |
|---|---|---|---|
| `max_session_minutes` | integer | Optional, default 90 | 30 to 180, multiple of 5. |

If you want zero preferences in the MVP, drop the object entirely and use a config constant (90). I recommend keeping the one field, because it gives you a meaningful, verifiable prompt variable at almost no cost.

### A.4 Derived values (computed by Python, not supplied by the student)

These are never accepted from the client; any such fields in the request are rejected or ignored.

- `end_date` = latest `exam_date`.
- `planning_dates` = every date from `start_date` through `end_date`, inclusive.
- `daily_limit_minutes` = `max_daily_hours` × 60 (integer).
- `last_study_date` per subject = `exam_date` − 1 day.
- `available_days` per subject = number of dates from `start_date` through `last_study_date`.
- `remaining_percent` per subject = 100 − `preparation_percent`.

### A.5 Input validation rules

1. Reject unknown top-level and subject fields (Pydantic `extra="forbid"`) so typos like `diffculty` fail loudly instead of being silently ignored.
2. Reject any unknown enum value rather than guessing.
3. Normalise before validating: trim, collapse internal whitespace, then check uniqueness.
4. `max_daily_hours` must be a multiple of 0.5. Store minutes internally to avoid float arithmetic.
5. Collect all field errors in one pass and return them together, each with a field path (e.g. `subjects[1].exam_date`).
6. Cross-field rules run only after field-level rules pass: exam date vs start date, uniqueness, and the planning-window cap.

### A.6 Representative input JSON

```json
{
  "start_date": "2027-03-01",
  "max_daily_hours": 4,
  "subjects": [
    {
      "name": "Alpha Studies",
      "exam_date": "2027-03-08",
      "difficulty": "hard",
      "preparation_percent": 35,
      "topics": ["Topic A", "Topic B", "Topic C"]
    },
    {
      "name": "Beta Basics",
      "exam_date": "2027-03-10",
      "difficulty": "medium",
      "preparation_percent": 60,
      "topics": []
    }
  ],
  "preferences": {
    "max_session_minutes": 90
  }
}
```

---

## B. LLM Output Schema

### B.1 Design principles

1. **Flat and small.** The model emits as little as possible. Everything derivable is computed by Python.
2. **One ordered list per day**, containing both study sessions and breaks, in the order the student should do them.
3. **No arithmetic from the LLM.** No totals, no weekday names, no counts.
4. **Closed vocabularies.** Enums for session type and kind, and exact-match subject names.
5. **Free text only where the LLM adds value:** the task description and short notes.

### B.2 Top-level object

| Field | Type | Required | Rules |
|---|---|---|---|
| `schema_version` | string | Yes | Must equal the expected constant (e.g. `"1.0"`). Detects prompt/schema drift. |
| `days` | array of Day | Yes | Must contain exactly one entry per planning date, in ascending order (see B.3). |
| `summary` | string | Yes | 1 to 500 characters. A short explanation of the approach. |
| `notes` | array of string | Optional, default `[]` | Max 5 items, each at most 200 characters. Scheduling rationale or caveats. |

### B.3 Day object

| Field | Type | Required | Rules |
|---|---|---|---|
| `date` | string, ISO date | Yes | Must match the expected planning date at that position. Unique. |
| `items` | array of Item | Yes | May be empty (a rest day or a day where nothing can be scheduled). Max 20 items. |

**Decision: the empty `items` array is the "no study" representation.** No `is_off_day` flag is needed. Rule 7 is satisfied because the date is still present.

### B.4 Item object (study session or break)

Using one list with a `kind` discriminator keeps ordering explicit and removes the awkward `after_session_order` linkage. In Pydantic this maps naturally to a discriminated union.

**Common fields**

| Field | Type | Required | Rules |
|---|---|---|---|
| `kind` | enum | Yes | `session` or `break` |
| `duration_minutes` | integer | Yes | Positive integer. For sessions: multiple of 5, between 15 and `max_session_minutes`. For breaks: multiple of 5, between 5 and 30. |

**Fields only for `kind = "session"`**

| Field | Type | Required | Rules |
|---|---|---|---|
| `subject` | string | Yes | Exact match to an input subject name (after normalisation). |
| `session_type` | enum | Yes | `new_learning`, `practice`, `revision`, `mock_test` |
| `task` | string | Yes | 5 to 200 characters. Specific activity description. |
| `topics` | array of string | Optional, default `[]` | Max 5. Each must be a topic from the student's list when that subject has topics. When the subject has none, this must be empty. |

**Fields only for `kind = "break"`:** none beyond the common fields. A `break` item must not contain `subject`, `session_type`, `task` or `topics`.

**Structural rules for breaks (hard, Python-checked):**
- A break must not be the first or last item of a day.
- No two consecutive breaks.
- Break minutes never count toward the daily study limit.

**Soft break guidance:** roughly one break after every 90-120 minutes of continuous study. This is a warning, not an error.

### B.5 Session types

| Value | Meaning | Notes |
|---|---|---|
| `new_learning` | First-time coverage of unprepared material | Should be rare or absent for subjects near 100% |
| `practice` | Exercises, problem solving, questions | Always allowed |
| `revision` | Reviewing already-covered material | The hard rule requires one per subject (with exceptions below) |
| `mock_test` | A timed test or past-paper style session | Soft expectation for hard subjects |

### B.6 Fields excluded from the LLM output (with justification)

| Field | Why excluded |
|---|---|
| Weekday name | Python derives it from `date` |
| Total minutes per day or subject | Python recomputes from items, so the LLM's own number would be ignored anyway |
| Start/end clock times | No clock availability was provided |
| `is_off_day` | Redundant with empty `items` |
| `order` number | Array position already is the order |
| Per-subject allocation | Python computes actual totals |
| Difficulty, exam date echoed back | Python already has them; echoing invites inconsistencies |

**Fields added by Python after validation** (in the API response to the frontend): `weekday`, `day_total_minutes`, `subject_totals`, `days_until_exam` per subject, `warnings[]`, `is_exam_date_for` (subjects whose exam falls on that date), and the generation metadata (prompt version, attempts used).

### B.7 Representative output JSON (structure only, fictional)

This is deliberately truncated to show the shape. It is not a real plan.

```json
{
  "schema_version": "1.0",
  "summary": "Illustrative summary text.",
  "notes": ["Illustrative note."],
  "days": [
    {
      "date": "2030-01-01",
      "items": [
        {
          "kind": "session",
          "subject": "Fictional Subject X",
          "session_type": "new_learning",
          "task": "Illustrative task description.",
          "topics": ["Fictional Topic 1"],
          "duration_minutes": 60
        },
        {
          "kind": "break",
          "duration_minutes": 10
        },
        {
          "kind": "session",
          "subject": "Fictional Subject Y",
          "session_type": "practice",
          "task": "Illustrative task description.",
          "topics": [],
          "duration_minutes": 45
        }
      ]
    },
    {
      "date": "2030-01-02",
      "items": []
    }
  ]
}
```

---

## C. Validation Strategy

### C.1 Three layers of responsibility

| Layer | Role | Reliability |
|---|---|---|
| Python input validation | Reject bad input before spending an API call | Enforced |
| LLM prompt instructions | Guide planning quality and task wording | Best effort, never trusted |
| Python output validation | Verify every hard rule on the returned JSON | Enforced |

### C.2 Python input validation (before the API call)

**Hard errors (request rejected, no LLM call):**
- Schema errors: missing fields, wrong types, unknown fields, out-of-range values, bad enums.
- Invalid or impossible dates.
- Duplicate subject names (after normalisation).
- Fewer than 1 or more than 8 subjects.
- Any `exam_date` that is not strictly after `start_date`.
- Planning window longer than the configured cap.
- Duplicate topics within a subject, and over-length strings.

**Feasibility checks (Python, before the API call):**
- A subject with remaining syllabus above 0% needs at least some minimum minutes. If cumulative capacity up to its `last_study_date` cannot cover the minimum for all subjects due by then, return an infeasible-plan error with suggestions (more hours, earlier start). The formula remains a planner concern, so it is not redefined here.
- A subject at 100% still needs a small revision floor, so it is included in the feasibility total.

**Warnings (request accepted):**
- Very tight capacity.
- A subject with `exam_date` only 1-2 days after `start_date`.
- A very high number of topics relative to the available days.

### C.3 Python output validation (after the API call)

**Structural checks (hard):**
- Valid JSON, `schema_version` matches, no unknown fields, required fields present, correct types, enums valid.
- `days` contains exactly the planning dates, once each, in ascending order.
- `kind` and its allowed fields are consistent (a break has no `subject`; a session has all required fields).

**Scheduling checks (hard):**

| ID | Rule | Source |
|---|---|---|
| O1 | Every session's subject is an input subject (exact match) | Rule 6 |
| O2 | No session for a subject on or after its `exam_date` | Rule 1 |
| O3 | Sessions of other subjects on that date are allowed | Rule 2 |
| O4 | Each day's total session minutes ≤ `daily_limit_minutes` | Rule 3 |
| O5 | Durations are positive integers; session minutes are multiples of 5 and within the min/max bounds | Rule 4 |
| O6 | Break minutes are excluded from study totals, and breaks are not first, last or consecutive | Rule 5 |
| O7 | Every planning date is present | Rule 7 |
| O8 | If a subject has topics, session `topics` must be a subset of them. If it has none, `topics` must be empty | Rules 8, 9 |
| O9 | Every subject has at least one `revision` session, unless its available days make that impossible (see edge cases) | Rule 10 |
| O10 | Every subject receives at least one session of any type, unless it has zero available days (impossible by input validation) | Coverage |

**Rule 9 limits, enforced approximately:** Python cannot detect "invented chapters" in free text. For subjects without topics, Python enforces that `topics` is empty and scans `task` text for conspicuous patterns such as "Chapter \d" or "Unit \d" as a soft warning. Reliable detection is not possible, so the prompt carries most of this rule and the warning provides a safety net.

**Soft checks (warnings only):**
- A day uses far below its limit while uncovered syllabus remains.
- More than 3 subjects on one day.
- No `mock_test` for hard subjects.
- Revision concentrated in a single day.
- More than 120 minutes of study without a break.
- Subject time far from the Python-computed recommended share.
- Suspicious "Chapter N" or "Unit N" wording where no topics were supplied.
- `summary` or `notes` over length (truncate rather than reject).

### C.4 What the prompt asks the LLM to do (best effort)

- Distribute time by need and urgency, using Python-supplied budgets.
- Put hard, low-preparation subjects first and interleave subjects.
- Place revision after learning, and a final revision near the exam.
- Use only provided topics, and use general activity wording otherwise.
- Write specific, actionable tasks.
- Self-check the daily totals.
- Return JSON only, matching the schema.

### C.5 Hard constraints versus soft preferences

| Hard (enforced, causes rejection or retry) | Soft (warning only) |
|---|---|
| Schema validity, enums, types | Balanced distribution |
| Date coverage, ordering, no duplicates | Spaced revision |
| Subject names exact | Hard subjects first |
| No session on or after the exam date | Mock tests for hard subjects |
| Daily limit | Break frequency |
| Duration integers, multiples of 5, bounds | Number of subjects per day |
| Break placement rules | Day utilisation |
| Topic subset rule | Task specificity |
| Revision present for each subject | Plan text length |

---

## D. Edge Cases and Recommended Handling

| # | Situation | Recommended handling |
|---|---|---|
| 1 | **Two subjects share an exam date** | Valid. Both stop on the day before. Both must still get revision in the same window, so feasibility is checked against the shared deadline. `is_exam_date_for` on the date lists both. |
| 2 | **Exam date equals `start_date`** | Reject with a clear error, because under rule 1 that subject can never be studied. Suggest changing the start date or removing the subject. (Alternative in unresolved decisions.) |
| 3 | **Exam the day after `start_date`** | Valid but warned as very tight. That subject has exactly one study day. Its single revision requirement (O9) must fit in that day. |
| 4 | **Very few daily hours (e.g. 0.5)** | Valid input. Feasibility check likely fails if several subjects are due soon, producing an infeasible-plan explanation. If feasible, require minimum session length 15 and accept a single short session per day. Warn if `max_session_minutes` exceeds the daily limit (clamp it to the daily limit in preprocessing). |
| 5 | **100% preparation** | Valid. The prompt instructs revision/practice/mock only (no `new_learning`). Python flags `new_learning` for such a subject as a soft warning. A small time floor is still required. |
| 6 | **0% preparation** | Valid. Largest share of time, `new_learning` expected. Soft warning in the input if the available days are fewer than a threshold, because the student may not cover everything. |
| 7 | **No syllabus topics** | Valid. The prompt tells the LLM to use general activities ("practice questions", "revise your notes") and forbids naming chapters. Output `topics` must be empty. Chapter-pattern scan raises a soft warning. |
| 8 | **Planning period contains days with no available study time** | In this MVP no day has zero capacity (no days-off feature), except that a day after all of a subject's... the window runs only to the last exam date, so every date has capacity. The only empty days arise if the LLM chooses to rest (allowed) or if no subject is still active on that date, which cannot happen because the window ends at the last exam date. Keep the empty `items` representation for rest days, and accept empty days. If days off are added later, `daily_limit_minutes` becomes per-day. |
| 9 | **LLM returns invalid JSON / truncated output** | Attempt tolerant extraction (strip code fences). If it still fails, count a validation failure and retry with feedback, within the retry cap. |
| 10 | **LLM returns missing fields** | Hard error; retry with feedback naming the exact field paths. |
| 11 | **LLM returns unexpected extra fields** | Strict mode rejects them. Recommended compromise for resilience: drop unknown *top-level optional commentary* fields with a logged warning, but reject unknown fields inside `items`, since those can mask a field confusion (e.g. a rogue `start_time`). Decide in the unresolved list. |
| 12 | **LLM exceeds the daily limit** | O4 error. Retry with the specific date and overage in the feedback. No automatic trimming, since removing a session may break revision coverage. Safe auto-repair is limited to normalisation (sorting, rounding to multiples of 5) and is logged. |
| 13 | **LLM schedules a subject on or after its exam date** | O2 error; retry. Optionally allow Python to *drop* offending sessions if that leaves all hard rules still satisfied, but I recommend retry rather than silent edits to keep behaviour predictable. |
| 14 | **LLM adds or renames a subject** | O1 error. Never fuzzy-match. Retry with the exact allowed names. |
| 15 | **LLM omits dates or skips a date** | O7 error. Retry. A common failure for long windows. |
| 16 | **LLM returns dates out of order or with duplicates** | Sorting is a safe auto-repair; duplicates are a hard error. |
| 17 | **Subject has a single available day and needs revision (O9)** | The single session may be of type `revision`. If feasibility said the capacity exists, this is satisfiable. |
| 18 | **A subject's topics are too many for its available time** | Input warning. The LLM prioritises, and the summary should say that coverage is partial. No error. |
| 19 | **Last exam far in the future** | Rejected by the window cap with a clear message ("plan up to N days at a time"). |
| 20 | **Total minutes slightly under the limit** | Valid. The limit is a maximum, so under-use is never an error. |
| 21 | **Subject name with special characters or very similar to another** | Normalised comparison catches case and whitespace duplicates. Names are treated as data in the prompt, and output matching is exact against the normalised input name. |

---

## E. Final Recommendations

### E.1 Recommended input JSON structure

```json
{
  "start_date": "YYYY-MM-DD",
  "max_daily_hours": 4,
  "subjects": [
    {
      "name": "string",
      "exam_date": "YYYY-MM-DD",
      "difficulty": "easy | medium | hard",
      "preparation_percent": 0,
      "topics": ["string"]
    }
  ],
  "preferences": {
    "max_session_minutes": 90
  }
}
```

Pydantic note: `preferences` is optional and defaults to `{max_session_minutes: 90}`. Use strict mode with extra fields forbidden.

### E.2 Recommended output JSON structure (LLM response)

```json
{
  "schema_version": "1.0",
  "summary": "string",
  "notes": ["string"],
  "days": [
    {
      "date": "YYYY-MM-DD",
      "items": [
        {
          "kind": "session",
          "subject": "string",
          "session_type": "new_learning | practice | revision | mock_test",
          "task": "string",
          "topics": ["string"],
          "duration_minutes": 60
        },
        {
          "kind": "break",
          "duration_minutes": 10
        }
      ]
    }
  ]
}
```

Pydantic note: `items` is a discriminated union on `kind`. Run structural validation first, then a separate pure-Python rules function (O1 to O10) that takes the parsed model and the preprocessed input.

### E.3 Fields to exclude from the MVP

- Days off, per-date hour overrides, break preferences, revision preference, time-of-day preference, free-text notes.
- Clock times, weekday names, daily totals, subject allocations, `order`, `is_off_day` in the LLM output.
- Any personal information (name, email, institution). The app is stateless and needs none.
- Per-topic difficulty or per-topic completion status. It is attractive, but it multiplies input complexity. Revisit after the MVP.
- Priority or weight overrides from the student. The planner derives priority internally.

### E.4 Unresolved decisions to finalise before implementation

| # | Decision | My recommendation |
|---|---|---|
| 1 | **Exam on `start_date`:** reject, or accept and silently skip that subject? | Reject. A silent skip would hide a likely typing mistake. |
| 2 | **Strictness on extra fields in LLM output** | Strict inside `items` and `days`; tolerant (ignore and log) at the top level only. |
| 3 | **Coercion at the API boundary:** accept `"40"` for `preparation_percent` and `"4"` for hours? | Strict at the Flask JSON API (the frontend sends proper types). Coerce only in the HTML form-handling layer. |
| 4 | **Session minimum/maximum values** (15 to `max_session_minutes`, break 5 to 30) | Adopt as stated, and keep them as config constants. |
| 5 | **Planning-window cap** (suggested 120 days) | Fix a number now, since it affects the `max_tokens` setting and the prompt size. |
| 6 | **Is a revision session mandatory for every subject (O9)?** Even with 100% prepared and one day left, or when the subject has a 1-day window | Yes, as a hard rule, with the single-day case accepted. Without it, "revision where appropriate" is unverifiable. |
| 7 | **Auto-repair scope:** which fixes may Python apply silently (sorting, rounding to 5), versus retry? | Limit repair to sorting and rounding. Never add, remove or retime sessions. |
| 8 | **Whether Python should drop offending sessions** (e.g. one session on an exam date) instead of retrying | Retry only, for predictability. Revisit if retry rates are high in live testing. |
| 9 | **Minimum-time floor per subject for feasibility** (e.g. 30 minutes of revision at 100%) | Pick constants in config now so the validator and planner agree. |
| 10 | **Topic matching:** exact (case-insensitive, whitespace-normalised) versus fuzzy | Exact after normalisation. Fuzzy matching risks accepting invented topics. |
| 11 | **Timezone for "not in the past" check** | Compare against the server's date with a 1-day tolerance, or drop this check. |
| 12 | **Days off in v1.1:** if likely, design `daily_limit_minutes` as a per-date map internally now | Yes. Build the planner around a per-date capacity map even though the MVP fills it with one constant. |

**Consistency check between the two schemas:** every output rule O1 to O10 uses only fields present in the input schema (`name`, `exam_date`, `topics`, `max_daily_hours`, `max_session_minutes`) and the derived values in A.4. No rule depends on data the LLM must supply about itself, so the validator can run entirely from the input and the LLM's `days` array.
