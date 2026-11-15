# Technical Requirements Specification: AI Timetable and Study Plan Generator

## 0. Guiding Principle: Who Decides What

The LLM is good at planning in natural language (topic breakdown, ordering, task wording) and unreliable at arithmetic, calendar logic and constraint satisfaction. The architecture follows from that.

| Responsibility | Owner |
|---|---|
| Parsing and validating user input | **Python** |
| Date arithmetic, list of available days, daily capacity | **Python** |
| Feasibility check (is the plan possible at all?) | **Python** |
| Priority weights and recommended hours per subject | **Python** (computed before the LLM call) |
| Choosing topics, ordering tasks, writing task descriptions | **LLM** |
| Placing revision sessions, interleaving subjects, rationale text | **LLM** |
| Checking every constraint in the output | **Python** (never trust the LLM) |
| Deciding to retry, repair or reject | **Python** |

**Key design decision:** Python precomputes facts and targets and passes them to the LLM, instead of asking the LLM to work them out. This shrinks the space of possible mistakes. Prompt instructions are treated as requests, and the Python validator as the enforcement.

---

## 1. Functional Requirements

| ID | Requirement |
|---|---|
| F1 | Accept student academic data through a web form (multiple subjects, dynamic add/remove). |
| F2 | Validate input on both client and server, with clear field-level error messages. |
| F3 | Run a feasibility analysis before calling the LLM and warn about tight or impossible situations. |
| F4 | Build the prompt dynamically from validated input and precomputed data. |
| F5 | Call the LLM API and receive a JSON timetable. |
| F6 | Parse and validate the JSON against schema and scheduling rules. |
| F7 | On validation failure, retry with error feedback (bounded), then fail gracefully. |
| F8 | Display the timetable day by day, with subject totals and any warnings. |
| F9 | Let the student download the timetable (JSON or CSV) or print it. |
| F10 | Show clear, non-technical error messages when generation fails. |

**Out of scope for v1 (to avoid complexity):** user accounts, database persistence, re-planning mid-schedule, calendar integrations, multi-user collaboration. The app stays stateless: request in, timetable out.

---

## 2. Input Requirements

### 2.1 Per-subject fields

| Field | Required | Type and rules |
|---|---|---|
| Subject name | Yes | 1-60 characters, unique (case-insensitive) within the request |
| Exam date | Yes | ISO date, must be on or after the study start date |
| Difficulty | Yes | Enum: `easy`, `medium`, `hard` |
| Preparation completed (%) | Yes | Integer 0-100 |
| Syllabus topics | Optional | List of topic names. If provided, tasks become far more specific; if absent, the LLM proposes generic topics |

### 2.2 Global fields

| Field | Required | Rules |
|---|---|---|
| Available study hours per day | Yes | Number, 0.5-16, in 0.5 steps |
| Study start date | Yes | ISO date, not in the past (configurable tolerance) |
| Preferences | Optional | See below |

### 2.3 Optional preferences (structured, not only free text)

- Days off (weekday checkboxes or specific dates)
- Hour overrides for specific dates (e.g. "only 2 hours on Saturday")
- Preferred maximum session length (30-180 min)
- Preferred break style (e.g. 10 min per 60-90 min of study)
- Revision preference (more or less revision)
- Study-time preference (morning/evening), used only as a label hint
- Free-text note (max 300 characters)

**Design decision:** Favour structured preferences over free text. Structured fields can be validated and enforced by Python. Free text can only be requested of the LLM and cannot be verified, so it must be labelled "soft, best effort" in the prompt and UI.

### 2.4 Input validation rules

- At least 1 subject, at most 8 (keeps output within token limits).
- Exam date before start date is a hard error.
- Preparation 100% is allowed (the subject then receives revision only).
- Reject unknown enum values rather than guessing.
- Free text is length-limited and stripped of control characters (see prompt-injection note in Section 4).

---

## 3. Output Requirements

### 3.1 Content requirements

Each day contains an ordered list of sessions. Each session has a subject, type, concrete task, and duration. Breaks are explicit entries. The timetable also carries a short summary and per-subject totals.

### 3.2 Design choices

- **Durations are integers in minutes**, never strings like "2.5 hrs". This makes validation arithmetic trivial.
- **Breaks are separate entries and do not count toward study hours.** This must be stated explicitly in the prompt and validated.
- **Session `type` is an enum**, so the frontend can colour-code revision sessions and Python can count them.
- **The LLM does not output weekday names or totals that Python can compute.** Python adds these after validation to avoid trusting the model's arithmetic.

### 3.3 Proposed JSON structure (schema outline, not data)

```
{
  "schema_version": "<string>",
  "summary": "<short overview, string>",
  "subject_allocation": [
    {
      "subject": "<exact subject name from input>",
      "planned_minutes": <integer>
    }
  ],
  "days": [
    {
      "date": "<YYYY-MM-DD>",
      "is_off_day": <boolean>,
      "sessions": [
        {
          "order": <integer, 1-based within the day>,
          "subject": "<exact subject name from input>",
          "type": "<new_learning | practice | revision | mock_test | light_review>",
          "task": "<specific task description, string>",
          "topics": ["<optional topic names>"],
          "duration_minutes": <integer>
        }
      ],
      "breaks": [
        {
          "after_session_order": <integer>,
          "duration_minutes": <integer>
        }
      ]
    }
  ],
  "notes": ["<scheduling rationale, strings>"]
}
```

### 3.4 Fields added by Python after validation (not requested from the LLM)

Weekday name, `total_study_minutes` per day, per-subject actual totals, and `warnings[]` (e.g. "Operating Systems received 12% less time than recommended").

---

## 4. Prompt Engineering Requirements

The prompt is assembled from a **versioned template** plus validated data. It should contain these sections, in this order:

1. **Role and task.** "You are a study planner. Produce a day-wise timetable as JSON only."
2. **Student data block.** Subjects, dates, difficulty, preparation %, and preferences, rendered as structured JSON inside clear delimiters.
3. **Python-precomputed facts.** These are the highest-value part of the prompt:
   - The exact list of dates in the planning window, with weekday and available minutes for each (including off days and overrides)
   - Days remaining before each exam
   - Remaining syllabus % per subject
   - A **recommended minutes budget per subject**, with tolerance (see Section 5)
4. **Hard rules** (numbered, unambiguous, phrased as "must/must not"), mirroring the validator exactly.
5. **Soft guidelines**: spaced revision, interleaving, hard subjects earlier in the day, honour preferences where possible.
6. **Revision policy**: for example, a full-revision session in the last 1-2 days before each exam, and light review only on exam days.
7. **Task-specificity instruction**: tasks must name topics or activities (e.g. "solve past-paper questions on X"), not "study Maths".
8. **Output contract**: the JSON schema outline, the enum values, and "no text outside the JSON, no markdown fences".
9. **One format-only example** using fictional subjects and dates different from the real request, so the model copies structure and not content.
10. **Self-check instruction**: "Before answering, verify that each day's total does not exceed its available minutes." (This helps, but is never relied upon.)

### 4.1 Additional prompt requirements

- **Prompt-injection defence.** Free-text preferences and subject names are untrusted. Wrap them in delimiters, instruct the model to treat them strictly as data, and rely on the validator as the real defence (any injected output still has to pass the schema and rules).
- **Settings:** low temperature (0.2-0.4) for consistency, and a `max_tokens` limit scaled to the number of days.
- **Retry prompt:** a second template that includes the previous invalid output (or a summary) plus the specific validation errors, asking for a corrected full JSON.
- **Prompt versioning:** store the template version in logs so output quality can be compared across prompt changes. This is also a good evaluation point for a prompt engineering project.

---

## 5. Scheduling Constraints

Constraints are split into **hard** (violation makes the timetable invalid) and **soft** (violation produces a warning only).

### 5.1 Hard constraints (Python-enforced)

| ID | Rule |
|---|---|
| H1 | Every date falls between the start date and the last exam date; each date appears at most once; dates are in ascending order. |
| H2 | Every subject name matches an input subject exactly. |
| H3 | No session for a subject after that subject's exam date. |
| H4 | On a subject's exam day, that subject may only have a `light_review` session, capped at a configurable maximum (e.g. 60 min). |
| H5 | Daily total study minutes must not exceed that day's available minutes (default hours, overridden by preferences). |
| H6 | Off days have zero sessions. |
| H7 | Every subject appears in the timetable at least once. |
| H8 | Every subject with remaining syllabus has at least one `revision` session before its exam date. |
| H9 | Session durations are positive integers, multiples of 5, between a min (e.g. 20) and max (e.g. 120 or the user's preference). |
| H10 | Breaks are positive integers and are not counted as study time. |
| H11 | Each subject's total planned time is within a tolerance (e.g. ±20%) of its recommended budget. |
| H12 | Output conforms to the JSON schema (required keys, types, enums). |

### 5.2 Soft constraints (warnings only)

| ID | Rule |
|---|---|
| S1 | Days should use at least ~90% of available time, except exam days and off days. |
| S2 | Revision should be spaced, not concentrated in one block. |
| S3 | Avoid more than 3 subjects in one day. |
| S4 | Hard subjects with low preparation should get priority in early slots. |
| S5 | A `mock_test` or past-paper session is expected for subjects rated hard. |
| S6 | Free-text preferences are honoured (cannot be verified automatically). |
| S7 | Break frequency is reasonable (e.g. at least one break per 120 minutes of continuous study). |

### 5.3 Priority and budget calculation (Python)

Suggested approach, deliberately simple:

- **Need score** per subject = remaining syllabus (100 - preparation %) × difficulty factor (e.g. easy 1.0, medium 1.25, hard 1.5).
- **Recommended minutes** = total available minutes split proportionally to need score, with a small floor per subject for revision.
- **Urgency adjustment (the main complexity risk):** an earlier exam limits how many hours a subject can receive before its deadline. Cap each subject's budget at the capacity available before its exam, and redistribute the excess to later-exam subjects.
- All weights and factors live in a config file, so they can be tuned and cited in project documentation.

### 5.4 Feasibility test (before calling the LLM)

Sort subjects by exam date. For each exam date, check that the **minimum required minutes of all subjects due on or before that date** is no more than the **cumulative capacity up to that date**. If not, the plan is infeasible no matter what the LLM does.

| Outcome | Behaviour |
|---|---|
| Comfortably feasible | Proceed |
| Feasible but very tight | Proceed with a visible warning |
| Infeasible | Do not call the LLM; show a clear explanation and suggestions (more hours, fewer off days, earlier start) |

This saves API cost and prevents the LLM from "hallucinating" an impossible plan.

---

## 6. Validation Requirements

### 6.1 What Python must independently verify

All hard constraints H1-H12, computed from the parsed JSON and the original input, never from numbers the LLM reports about itself. Also:

- Valid JSON (after stripping code fences or stray text as a tolerance step)
- No extra or missing required keys
- Recomputed daily totals and subject totals

### 6.2 Validation result structure

The validator returns a report with a list of `errors` (hard violations, each with rule ID, date, subject and message) and `warnings` (soft violations). This structure feeds both the retry prompt and the UI.

### 6.3 Handling an invalid timetable

A bounded, ordered strategy:

1. **Auto-repair trivial issues** in Python, only where the fix is unambiguous and safe: sorting days and sessions, re-numbering `order`, rounding durations to the nearest 5. Record each repair as a warning.
2. **Retry with feedback:** re-prompt with the specific error list (maximum 2 retries, so at most 3 LLM calls per request).
3. **Fallback decision:** if still invalid, return an error to the user with a readable explanation. Optional stretch goal: a simple deterministic Python fallback planner (proportional split, round-robin) clearly labelled "basic plan, AI generation failed".
4. **Never silently show an invalid timetable.** The UI should only render timetables that passed hard validation.

**Justification:** Retry-with-feedback is cheap to implement and effective, because LLMs usually fix specific, named errors. The retry cap bounds cost and latency.

---

## 7. Backend Architecture

### 7.1 Proposed modules

| Module | Responsibility |
|---|---|
| `app` (Flask factory and routes) | HTTP handling only: parse request, call the service, return JSON or HTML. No business logic. |
| `config` | Environment-based settings: API key, model name, timeouts, retry limits, constraint thresholds, difficulty weights, prompt version. |
| `models` (schemas) | Typed definitions for the student request, timetable, and validation report. Dataclasses or Pydantic (Pydantic recommended for built-in validation and error messages). |
| `input_validator` | Applies the input rules in Section 2 and produces field-level errors. |
| `planner` (preprocessor) | Builds the date list, daily capacities, remaining-syllabus values, priority scores, budgets, and the feasibility result. Pure functions, no I/O. |
| `prompt_builder` | Renders the versioned templates from planner output. Also builds the retry prompt. |
| `llm_client` | Single point of contact with the LLM API: sends the prompt, handles timeouts and retries, returns raw text. Provider-agnostic interface. |
| `response_parser` | Extracts JSON from the raw text and maps it to the timetable model. |
| `timetable_validator` | Implements H1-H12 and S1-S7 and returns a validation report. Pure functions. |
| `generation_service` (orchestrator) | Coordinates the pipeline: validate input, plan, build prompt, call LLM, parse, validate, retry/repair, enrich. The only module that knows the whole flow. |
| `errors` | Custom exceptions (e.g. `InvalidInputError`, `InfeasiblePlanError`, `LLMUnavailableError`, `InvalidTimetableError`) mapped to HTTP status codes. |
| `templates/`, `static/` | Frontend files. |
| `tests/` | Unit and integration tests. |

### 7.2 Request flow

```
Browser form → POST /api/generate
  → input_validator → planner (feasibility, budgets)
  → prompt_builder → llm_client → response_parser
  → timetable_validator ──invalid──→ repair / retry (loop, bounded)
  → enrich (weekdays, totals, warnings) → JSON response → render
```

### 7.3 Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | Serves the single-page UI |
| `POST /api/generate` | Accepts the input JSON and returns the validated timetable, or a structured error |
| `GET /api/health` | Simple liveness check (optional, helpful for deployment) |

### 7.4 Design justifications

- `planner` and `timetable_validator` are pure functions and are the most testable and valuable parts. They can be fully tested without an API key.
- `llm_client` is isolated so that the LLM can be swapped or mocked without touching other modules.
- The orchestrator keeps routes thin, so the pipeline can be run from a script or test without Flask.

---

## 8. API Integration

### 8.1 Communication requirements

- The API key is read from an environment variable and **never** sent to the frontend or committed to source control.
- The backend makes a single request per generation attempt: system and user messages, low temperature, and an explicit `max_tokens` limit.
- If the provider offers a structured-output or JSON mode, use it. It reduces parse failures but does not replace validation.
- Set an explicit request timeout (e.g. 45-60 seconds, since long timetables take time to generate).

### 8.2 Failure handling

| Failure | Handling |
|---|---|
| Network error or timeout | Retry with exponential backoff (e.g. 2 retries) |
| Rate limit (429) | Backoff, honouring the retry-after header if present |
| Server error (5xx) | Retry with backoff |
| Auth error (401/403) | No retry; log the configuration error; show a generic "service unavailable" message to the user |
| Output truncated (token limit hit) | Treat as invalid output; retry, ideally with a more compact format or a larger limit |
| Non-JSON or malformed JSON | Attempt a tolerant extraction (strip fences/prose); otherwise count as a validation failure and retry |
| Refusal or empty response | Retry once, then fail gracefully |

### 8.3 Two separate retry budgets

- **Transport retries** (network, 429, 5xx) handled inside `llm_client`.
- **Validation retries** (bad content) handled by the orchestrator.

Keeping them separate prevents one failure type from exhausting the other's budget. Also set an overall cap on LLM calls per request to control cost.

### 8.4 Other requirements

- Log the prompt version, attempt number, latency, token usage and validation error codes. Do not log full student data or the API key.
- Basic rate limiting per client on `/api/generate` to protect API spend.
- Because generation can take many seconds, the frontend must show a loading state. A synchronous request is acceptable for a student project; background jobs and polling are unnecessary complexity.

---

## 9. Frontend Requirements

### 9.1 Input form

- Subject rows with: name, exam date (date picker), difficulty (dropdown), preparation % (slider with numeric display), optional topics (comma-separated or tag input), plus add/remove row buttons.
- Global fields: daily study hours, start date.
- Collapsible "Preferences (optional)" section: days off, per-date overrides, max session length, break style, free-text note.
- Inline validation messages, with the submit button disabled while invalid. Client checks mirror the server rules for convenience only; **the server remains authoritative**.
- Date inputs should enforce `min` attributes (e.g. exam date not before start date).

### 9.2 States

Loading (spinner and "this may take up to a minute" text), success, validation error (field-level), infeasible-plan explanation, and generation failure (with a retry button that keeps the form data).

### 9.3 Timetable display

- **Summary banner:** plan overview, total hours, days covered.
- **Warnings panel** (if any) above the timetable, visually distinct.
- **Subject totals:** planned hours per subject (a simple bar or table).
- **Day-wise view:** one card or table block per date, showing weekday, date, sessions in order (subject, task, duration, type badge) and breaks. Off days are visibly marked.
- **Visual cues:** a consistent colour per subject, distinct badges for revision and mock tests, and highlighted exam days with a countdown to the exam.
- **Actions:** print-friendly CSS, download as JSON and CSV, and "edit inputs and regenerate".
- **Accessibility and responsiveness:** works on mobile (students often use phones), with sufficient contrast so colour is never the only cue.

### 9.4 Implementation notes

Plain HTML/CSS/JavaScript with `fetch` to the JSON endpoint; no framework is needed. Render all LLM-provided text with `textContent` (not `innerHTML`) to avoid XSS from model output.

---

## 10. Testing Requirements

### 10.1 General approach

- **Unit-test the pure modules heavily** (`planner`, `timetable_validator`, `input_validator`, `prompt_builder`).
- **Mock the LLM client** in all automated tests, returning canned good and bad outputs. Tests must never need a live API key.
- Keep a small, separate set of manual or optional live-LLM evaluations to compare prompt versions.

### 10.2 Normal inputs

| Case | Expected result |
|---|---|
| 3 subjects, staggered exam dates, typical hours | Passes validation, all subjects covered |
| Single subject | Valid plan; no interleaving needed |
| Subject at 100% prepared | Revision-only sessions |
| Subject at 0% prepared | Receives the largest share |
| Exam dates on consecutive days | Valid; the exam-day rules apply to each |
| Preferences with days off | No sessions on those dates |

### 10.3 Incomplete or invalid inputs

| Case | Expected result |
|---|---|
| Missing subject name, date, or difficulty | Field-level error; no LLM call |
| Zero subjects | Error |
| Duplicate subject names | Error |
| Preparation 105% or -5% | Error |
| Non-numeric or negative hours | Error |
| Malformed dates (e.g. 31-02-2026) | Error |
| Very long free-text or special characters | Truncated or rejected, never crashes |
| Free-text containing "ignore previous instructions" | Still produces a validated timetable |

### 10.4 Conflicting constraints

| Case | Expected result |
|---|---|
| Exam date before start date | Hard error |
| Two exams on the same date | Valid if feasible; otherwise warning or error |
| Not enough hours for the remaining syllabus | Infeasibility explanation, no LLM call |
| Every day off before an exam | Infeasibility error |
| Daily hours overridden to 0 on most days | Infeasible or warning, depending on capacity |
| Exam tomorrow with 0% preparation | Feasible-but-tight warning, or infeasible if the daily hours are too small |
| Start date equals exam date | Edge case: exam-day rules only |

### 10.5 LLM-failure and validator tests (with mocked responses)

| Mocked LLM behaviour | Expected system behaviour |
|---|---|
| Valid JSON, valid plan | Accepted |
| JSON wrapped in markdown fences or prose | Extracted and accepted |
| Truncated JSON | Retry |
| Invented subject name | H2 error, retry with feedback |
| Study session after a subject's exam | H3 error, retry |
| Daily total exceeds available hours | H5 error, retry |
| Wrong arithmetic in self-reported totals | Ignored; Python's recomputed totals are used |
| Missing revision for a subject | H8 error |
| Always invalid output | After max retries, graceful failure; the user never sees an invalid plan |
| Timeout then success | Transport retry works |
| 401 error | No retry, generic user message |
| Fix succeeds on retry 1 | Final plan accepted, attempt count logged |

### 10.6 Additional tests

- **Prompt builder snapshot tests:** the prompt contains all subjects, all dates, the budgets, and the rules.
- **Budget calculation tests:** proportions are sensible, and the urgency cap redistributes correctly.
- **End-to-end test** through the Flask test client with a mocked LLM.
- **Frontend manual checklist:** form validation, mobile layout, print view, error states.

---

## 11. Non-Functional Requirements

| Area | Requirement |
|---|---|
| Security | API key in environment variables only; input length limits; output escaped in the browser; basic rate limiting |
| Privacy | Do not log full student data; no persistence in v1 |
| Performance | Target under ~60 seconds end to end; show progress feedback |
| Cost control | Capped retries, capped `max_tokens`, feasibility check before calling the LLM |
| Maintainability | Thresholds and weights in config, versioned prompts, pure functions for core logic |
| Observability | Structured logs with attempt counts and validation error codes |

---

## 12. Proposed Development Sequence

| Phase | Work | Why in this order |
|---|---|---|
| **1** | Finalise the JSON schema, constraint list and config values (this document) | Everything depends on these contracts |
| **2** | Data models and `input_validator`, with tests | Establishes trustworthy input |
| **3** | `planner`: date list, capacity, priority scores, budgets, feasibility, with tests | Pure logic; no API needed |
| **4** | `timetable_validator` (H1-H12, S1-S7), with tests using hand-written good and bad timetables | Defines "correct" before any LLM is involved |
| **5** | `prompt_builder` and the response parser, with snapshot tests | Still no network needed |
| **6** | `llm_client` with mock mode, then the real API connection, timeouts and backoff | Integrate the unreliable component late |
| **7** | `generation_service` orchestrator: retry-with-feedback, auto-repair, enrichment, plus end-to-end tests with mocked failures | The core pipeline is complete |
| **8** | Flask routes and error mapping | Thin layer over a working service |
| **9** | Frontend: form, validation, loading, results display, export | UI against a stable API |
| **10** | Live-LLM evaluation: run varied scenarios, tune the prompt and weights, record the failure rate per prompt version | The prompt-engineering part of the project |
| **11** | Polish: warnings UI, print CSS, rate limiting, documentation | Final hardening |
| **12 (optional)** | Deterministic fallback planner; comparison report of prompt versions | Stretch goals |

**Why this order:** the validator and planner are built and tested before the LLM is touched, so you have an objective definition of "correct" and an offline test suite. When live-LLM testing starts, every failure is classified by the validator's rule IDs, which gives you measurable data on how each prompt revision changes the failure rate.