Technical Requirements Specification
AI-Powered Timetable and Study Plan Generator
Software Architecture
Python + Flask
LLM Integration
Prompt Engineering Project

Document Type: Software Requirements & System Design Specification
Project Stage: Planning and Architecture
Implementation Status: Not started

1. Project Overview
1.1 Problem Statement
Students often struggle to create effective study schedules because they need to consider multiple variables simultaneously:
- Different examination dates.
- Different subject difficulty levels.
- Different preparation percentages.
- Limited daily study hours.
- Individual study preferences.
- Revision requirements before examinations.
A manually created timetable may not distribute study time effectively or account for changing priorities as examination dates approach.

The proposed application will use a Large Language Model (LLM) to analyze student information and generate a personalized, day-wise study timetable.

However, the application will not blindly trust the LLM. Python will independently validate the generated timetable against predefined scheduling rules before presenting it to the student.
1.2 Project Goals
The application should:
1. Collect academic information from students.
2. Analyze preparation requirements and examination deadlines.
3. Dynamically construct an LLM prompt using student inputs.
4. Generate a structured timetable in JSON format.
5. Validate the generated timetable using Python.
6. Correct or regenerate invalid responses where possible.
7. Display the final timetable through an interactive web interface.
1.3 Proposed Technology Stack
Component	Technology	Responsibility
Programming language	Python	Backend logic and validation
Backend framework	Flask	HTTP requests and application routing
AI integration	LLM API	Study planning and task generation
Prompt engineering	Python	Dynamic prompt construction
Data format	JSON	Structured AI output
Frontend	HTML	Page structure
Styling	CSS	User interface
Frontend logic	JavaScript	Form handling and dynamic rendering
Data validation	Python	Constraint verification
Testing	Pytest	Unit and integration testing

Architectural recommendation: Start with a modular monolithic Flask application rather than microservices. Your project does not need the additional deployment and communication complexity of multiple independent services.

2. Functional Requirements
Functional requirements describe what the application must actually do.

The system should contain the following features.
FR-01: Student Information Collection
The application must provide a form through which students can enter their academic information.

The form should support multiple subjects, with each subject having its own examination date, difficulty and preparation percentage.
FR-02: Input Validation
Before sending information to the LLM, the backend must verify:
- Required fields are present.
- Examination dates are valid.
- Preparation percentages are between 0 and 100.
- Study hours are positive.
- Examination dates fall within the supported planning period.
- Subject names are not empty or duplicated unintentionally.
Invalid inputs should produce meaningful error messages.
FR-03: Study Priority Analysis
The application should determine which subjects require greater attention.

The LLM can consider:
- Examination proximity.
- Subject difficulty.
- Preparation percentage.
- Remaining syllabus.
- Available study time.
Python may calculate basic priority indicators to provide the LLM with additional structured context.

For example:
\[
\text{Remaining Preparation} = 100 - \text{Preparation Percentage}
\]

The LLM should make the final planning decisions, subject to Python validation.
FR-04: Dynamic Prompt Construction
The backend must construct an LLM prompt dynamically using the information submitted by the student.

The prompt must change according to:
- Number of subjects.
- Examination dates.
- Available study hours.
- Preparation levels.
- Student preferences.
It should not use a fixed timetable prompt containing hardcoded subject information.
FR-05: AI Timetable Generation
The application must send the dynamically constructed prompt to an LLM API.

The LLM must return a structured timetable containing daily study sessions, tasks, durations and revision activities.
FR-06: Independent Timetable Validation
Python must verify the generated timetable before displaying it.

The LLM must not be treated as the authority for whether scheduling constraints have been satisfied.
FR-07: Error Handling and Regeneration
If the LLM generates an invalid timetable:
1. Identify the validation errors.
2. Send the errors back to the LLM with the original planning requirements.
3. Request a corrected timetable.
4. Validate the corrected response again.
5. If validation still fails, return a meaningful error instead of displaying an invalid timetable.
Limit the number of regeneration attempts to avoid excessive API usage.
FR-08: Timetable Display
The application must display the validated timetable in a structured, readable format.

Students should be able to see:
- Daily study schedules.
- Subject-wise study tasks.
- Study durations.
- Revision sessions.
- Breaks.
- Total daily study hours.
FR-09: Timetable Persistence (Optional for MVP)
Students may eventually be able to save and retrieve previously generated timetables.

This is not essential for the first version.

A database can be introduced in a later development stage.

3. Input Requirements
The input system should be designed to support multiple subjects dynamically rather than accepting a fixed number of subjects.

I recommend dividing the input form into three sections.
3.1 Student-Level Inputs
These fields apply to the entire timetable.
Field	Data type	Mandatory?	Validation
Available study hours per day	Float	Yes	Greater than 0
Study start date	Date	Yes	Valid date
Student name	String	No	Non-empty if provided
Preferred study time	Enum	No	Morning/Afternoon/Evening/Flexible
Preferred session duration	Integer	No	Positive, reasonable duration
Preferred break duration	Integer	No	Positive duration
Days unavailable	List of dates	No	Valid dates within planning period
Additional instructions	String	No	Length limit

3.2 Subject-Level Inputs
Students must be able to add multiple subjects.
Field	Data type	Mandatory?	Validation
Subject name	String	Yes	Cannot be empty
Examination date	Date	Yes	Must not precede study start date
Difficulty	Enum	Yes	Easy/Medium/Hard
Preparation percentage	Integer	Yes	0–100
Syllabus/topics	List of strings	No	Valid topic names
Important topics	List of strings	No	Must belong to subject
Topic-wise completion	List/object	No	Valid percentages

Important recommendation: Add syllabus topics as an optional field, even though they weren't part of your initial requirements.

Why?

Suppose a student enters Mathematics with 40% preparation.

The LLM knows that 60% remains, but it does not know which chapters are incomplete.

Without syllabus information, it might generate generic tasks such as:
- Complete pending Mathematics chapters.
- Practice important numerical problems.
- Revise difficult concepts.
With syllabus information, it can generate specific tasks such as:
- Complete integration.
- Practice differential equations.
- Revise matrices.
This significantly improves personalization.
3.3 Subject Input Example
The backend should receive information in a structure similar to this:
{
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
    }
  ],
  "available_hours_per_day": 4,
  "start_date": "2026-11-16",
  "preferences": {
    "preferred_study_time": "Flexible",
    "session_duration": 60,
    "break_duration": 10
  }
}


This is an example of the data your frontend will send to Flask.
3.4 Input Design Recommendations
- Use a date picker for examination dates.
- Use dropdowns for difficulty levels.
- Use a slider or number input for preparation percentage.
- Use an Add Subject button to dynamically create subject entries.
- Allow students to remove subjects.
- Provide an optional preferences section that can be expanded when needed.
Do not make every preference mandatory. Too many required fields will make the application unnecessarily difficult to use.

4. Output Requirements
The output must be structured, predictable and easy for Python to process.

I recommend using a hierarchical JSON structure.
4.1 Expected Timetable Components
Each generated timetable should contain:
Component	Description
Date	Date of the study schedule
Day	Day of the week
Subject	Subject being studied
Task	Specific activity to complete
Duration	Planned study duration
Start time	Expected beginning of the session
End time	Expected end of the session
Session type	Learning/Practice/Revision/Mock Test
Breaks	Rest periods between sessions
Daily total	Total study time for that day

4.2 Proposed JSON Structure
This is the recommended output contract between the LLM and your backend.
{
  "timetable": {
    "start_date": "2026-11-16",
    "end_date": "2026-11-25",
    "total_days": 10,
    "days": [
      {
        "date": "2026-11-16",
        "day": "Monday",
        "sessions": [
          {
            "subject": "Mathematics",
            "task": "Complete integration concepts",
            "session_type": "Learning",
            "start_time": "09:00",
            "end_time": "10:00",
            "duration_minutes": 60
          },
          {
            "subject": "Mathematics",
            "task": "Practice integration problems",
            "session_type": "Practice",
            "start_time": "10:10",
            "end_time": "11:10",
            "duration_minutes": 60
          }
        ],
        "breaks": [
          {
            "start_time": "10:00",
            "end_time": "10:10",
            "duration_minutes": 10
          }
        ],
        "total_study_minutes": 120
      }
    ]
  }
}


The above is a structural example, not an actual study timetable.
4.3 Why This Structure?
There are several reasons for using this format.

1. Hierarchical organization

The timetable contains multiple days, and each day contains multiple study sessions.

2. Easy Python processing

You can iterate through the days and sessions to validate durations and scheduling constraints.

3. Frontend compatibility

JavaScript can easily convert this JSON into tables, cards or calendar views.

4. Extensibility

You can introduce additional properties later, such as:
- Session completion status.
- Priority level.
- Study notes.
- Topic identifiers.
4.4 Important Design Decision: Minutes Instead of Hours
Internally, store durations as integer minutes.

For example:
- 30 minutes = 30
- 1 hour = 60
- 1.5 hours = 90
This makes duration calculations easier and avoids floating-point errors.

The frontend can convert minutes into human-readable hours and minutes.

5. Prompt Engineering Requirements
This is one of the most important components of your project.

Your application is not simply sending student information to an AI model. It is dynamically constructing a carefully designed instruction that guides the model toward a useful and structured result.
5.1 Prompt Architecture
I recommend dividing the prompt into five sections.
1. System Role

Defines the AI's responsibility as an academic study planner.


2. Student Information

Injects the student's subjects, dates, difficulty and preparation levels.


3. Scheduling Instructions

Defines prioritization, study allocation, revision and break requirements.


4. Output Requirements

Defines the exact JSON structure and permitted values.


5. Constraint Instructions

Reminds the LLM of scheduling rules that Python will independently verify.


5.2 System Role
The system instruction should establish the model's role.

For example:

"You are an expert academic study planner. Your responsibility is to create realistic, personalized and examination-oriented study schedules based on student information."

It should also instruct the model to:
- Prioritize subjects intelligently.
- Distribute study hours appropriately.
- Include sufficient revision.
- Avoid unrealistic study sessions.
- Generate specific study tasks.
5.3 Dynamic Student Information
The backend must inject student information into the prompt.

The prompt should include:
- Subject names.
- Examination dates.
- Difficulty levels.
- Preparation percentages.
- Available study hours.
- Planning start date.
- Optional preferences.
- Syllabus topics, if provided.
This information should be inserted dynamically rather than hardcoded.
5.4 Scheduling Instructions
The LLM should receive explicit instructions regarding:
1. How to prioritize subjects.
2. How to distribute study hours.
3. How to allocate time to incomplete subjects.
4. How to handle examination dates.
5. When to schedule revision.
6. When to schedule mock tests.
7. How to distribute breaks.
8. How to accommodate preferences.
An important distinction:

A subject with low preparation should generally receive more attention, but examination proximity must also influence its priority.

Do not use preparation percentage as the only scheduling factor.
5.5 Output Instructions
The prompt must specify:
- Return valid JSON only.
- Follow the predefined JSON schema.
- Do not include Markdown fences.
- Use ISO date format (YYYY-MM-DD).
- Use 24-hour time format.
- Use integer minutes for durations.
- Include every date in the planning period.
- Do not invent syllabus topics when none are supplied.
Ideally, use the LLM provider's structured output or JSON Schema functionality, if available.

This reduces formatting errors but does not replace Python validation.
5.6 Constraint Instructions
The prompt should explicitly state that:
- Daily study time must not exceed available hours.
- Sessions must not overlap.
- All relevant subjects must receive preparation time.
- Revision must occur before examinations.
- Examination-day scheduling must respect the examination timing if supplied.
- Breaks should be placed between appropriate sessions.
Remember: these are instructions to the LLM, not guarantees.

Python remains responsible for enforcing the constraints.

6. Scheduling Constraints
This section defines the actual rules your application should enforce.

I recommend dividing constraints into mandatory and recommended rules.
6.1 Mandatory Constraints
ID	Constraint	Description
SC-01	Date validity	Every timetable date must fall within the planning period.
SC-02	Daily hour limit	Total study duration must not exceed available daily hours.
SC-03	No overlapping sessions	Two study sessions cannot occupy the same time.
SC-04	Valid subjects	Every session must refer to a submitted subject.
SC-05	Positive duration	Every study session must have a positive duration.
SC-06	Valid examination dates	A subject's study sessions must not occur after its examination.
SC-07	Valid time sequence	End time must be later than start time.
SC-08	Break consistency	Breaks cannot overlap study sessions.
SC-09	Complete date coverage	Every date in the planning period must have a timetable entry.
SC-10	Subject coverage	Every subject must receive appropriate preparation before its exam.

One important exception: a student's examination may occur on the same day as a study session. The application should support a configurable examination-day policy.

For the MVP, I recommend excluding examination preparation sessions after the examination has occurred. Whether to allow a short pre-exam revision session should be configurable.
6.2 Recommended Constraints
These are planning recommendations rather than absolute rules.
- Divide long study periods into manageable sessions.
- Include breaks after extended study periods.
- Allocate revision sessions closer to examinations.
- Allocate more time to difficult and less-prepared subjects.
- Avoid introducing too many new topics on the day before an examination.
- Include mock tests where sufficient preparation time exists.
- Avoid assigning all available hours to one subject repeatedly.
6.3 Subject Priority Calculation
You can eventually introduce a simple Python-based priority score.

One possible formula is:
\[
P = w_1(100-C) + w_2D + w_3T
\]

Where:
- \(C\) = Preparation percentage.
- \(D\) = Difficulty score.
- \(T\) = Examination urgency score.
- \(w_1,w_2,w_3\) = Configurable weights.
For example:
Variable	Possible scoring
Preparation	100 - completion percentage
Difficulty	Easy = 1, Medium = 2, Hard = 3
Exam urgency	Higher score for nearer examinations

Normalize the values before combining them.

My recommendation: Keep this priority score optional in the first version. Let the LLM make the initial allocation decisions, then use Python to enforce scheduling constraints. Later, compare AI-generated allocations with a rule-based baseline.

This gives you an opportunity to evaluate whether prompt engineering actually improves planning quality.

7. Validation Requirements
This is a critical architectural component.

Your application must have two separate validation stages.
Stage 1: LLM generation

The AI generates the timetable based on the prompt.


Stage 2: Python validation

Python independently checks the JSON structure and scheduling constraints.


Valid

Display timetable


Invalid

Attempt correction




7.1 Input Validation
Before calling the LLM, Python should check:
- Required fields.
- Data types.
- Date formats.
- Valid percentages.
- Valid difficulty values.
- Positive study hours.
- Valid subject names.
- Examination date ordering.
This avoids unnecessary API calls.
7.2 JSON Validation
After receiving the LLM response, Python should verify:
- Response is valid JSON.
- Required keys exist.
- Correct data types are used.
- Dates follow the expected format.
- Session types belong to permitted values.
- Durations are positive integers.
- Subject names match the submitted subjects.
I recommend using Pydantic for defining and validating your data models.

It is particularly useful because it separates structural validation from scheduling logic.
7.3 Scheduling Validation
Python should independently calculate:

A. Daily study duration
\[
H_d = \sum_{i=1}^{n} \text{Duration}_i
\]

Verify:
\[
H_d \leq H_{\text{available}}
\]

B. Session overlap

For any two sessions A and B:
\[
A_{\text{start}} < B_{\text{end}}
\]

and
\[
B_{\text{start}} < A_{\text{end}}
\]

If both are true, the sessions overlap.

C. Subject validity

Every generated session must reference a subject submitted by the student.

D. Examination deadline

No preparation session should be scheduled after the corresponding examination.

E. Break validation

Check that breaks are valid, non-overlapping and placed between study sessions.

F. Date coverage

Ensure the timetable contains every expected planning date.

G. Daily total consistency

The reported daily total must equal the sum of its study session durations.
7.4 What Happens When Validation Fails?
I recommend the following recovery process:
Attempt	Action
First response	Validate the generated JSON
First failure	Collect specific validation errors
Regeneration	Send errors and original requirements back to the LLM
Second response	Validate again
Second failure	Allow one final correction attempt or stop
Final failure	Return a user-friendly error

Set a maximum of two or three generation attempts.

Do not create an endless retry loop.

Also, do not silently discard invalid sessions or reduce durations without informing the student. That could produce a timetable different from the one the AI intended.

8. Backend Architecture
I recommend a modular Flask backend.

You do not need a complicated architecture with multiple servers or microservices.

Instead, divide the application into independent Python modules.
8.1 Proposed Project Structure
study_planner/
│
├── app.py
│
├── config.py
│
├── routes/
│   ├── __init__.py
│   └── timetable_routes.py
│
├── services/
│   ├── input_service.py
│   ├── priority_service.py
│   ├── prompt_service.py
│   ├── llm_service.py
│   ├── validation_service.py
│   └── timetable_service.py
│
├── models/
│   ├── student.py
│   └── timetable.py
│
├── templates/
│   ├── index.html
│   └── timetable.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── tests/
│   ├── test_input.py
│   ├── test_prompt.py
│   ├── test_validation.py
│   └── test_timetable.py
│
├── requirements.txt
│
└── .env


This is a proposed structure, not an implementation requirement that every file must be created immediately.
8.2 Module Responsibilities
Module	Responsibility
app.py	Initialize Flask application
config.py	Manage configuration
timetable_routes.py	Handle frontend requests and responses
input_service.py	Validate and normalize student inputs
priority_service.py	Calculate optional subject priority scores
prompt_service.py	Dynamically construct LLM prompts
llm_service.py	Communicate with the LLM API
validation_service.py	Validate AI-generated timetable
timetable_service.py	Coordinate generation, correction and final output
student.py	Define student input data models
timetable.py	Define timetable output data models

8.3 Backend Request Flow
#chatgpt-mermaid-_r_u1_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-_r_u1_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_u1_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_u1_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-_r_u1_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-_r_u1_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-_r_u1_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-_r_u1_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-_r_u1_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-_r_u1_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-_r_u1_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-_r_u1_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-_r_u1_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-_r_u1_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-_r_u1_ p{margin:0;}#chatgpt-mermaid-_r_u1_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-_r_u1_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-_r_u1_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-_r_u1_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-_r_u1_ .label text,#chatgpt-mermaid-_r_u1_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-_r_u1_ .node rect,#chatgpt-mermaid-_r_u1_ .node circle,#chatgpt-mermaid-_r_u1_ .node ellipse,#chatgpt-mermaid-_r_u1_ .node polygon,#chatgpt-mermaid-_r_u1_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-_r_u1_ .rough-node .label text,#chatgpt-mermaid-_r_u1_ .node .label text,#chatgpt-mermaid-_r_u1_ .image-shape .label,#chatgpt-mermaid-_r_u1_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-_r_u1_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-_r_u1_ .rough-node .label,#chatgpt-mermaid-_r_u1_ .node .label,#chatgpt-mermaid-_r_u1_ .image-shape .label,#chatgpt-mermaid-_r_u1_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-_r_u1_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-_r_u1_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-_r_u1_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-_r_u1_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-_r_u1_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-_r_u1_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-_r_u1_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-_r_u1_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-_r_u1_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-_r_u1_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-_r_u1_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-_r_u1_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-_r_u1_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-_r_u1_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-_r_u1_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-_r_u1_ .icon-shape,#chatgpt-mermaid-_r_u1_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-_r_u1_ .icon-shape p,#chatgpt-mermaid-_r_u1_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-_r_u1_ .icon-shape .label rect,#chatgpt-mermaid-_r_u1_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-_r_u1_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-_r_u1_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-_r_u1_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-_r_u1_ [data-look="neo"].node rect,#chatgpt-mermaid-_r_u1_ [data-look="neo"].cluster rect,#chatgpt-mermaid-_r_u1_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-_r_u1_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_u1_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-_r_u1_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-_r_u1_-gradient);stroke-width:1px;}#chatgpt-mermaid-_r_u1_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_u1_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-_r_u1_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-_r_u1_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_u1_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-_r_u1_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-_r_u1_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_u1_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-_r_u1_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_u1_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-_r_u1_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-_r_u1_ .node tspan[font-weight="normal"],#chatgpt-mermaid-_r_u1_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-_r_u1_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-_r_u1_ .node rect,#chatgpt-mermaid-_r_u1_ .node circle,#chatgpt-mermaid-_r_u1_ .node ellipse,#chatgpt-mermaid-_r_u1_ .node polygon,#chatgpt-mermaid-_r_u1_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-_r_u1_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-_r_u1_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-_r_u1_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-_r_u1_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-_r_u1_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Student submits formFlask RouteInput ValidationInput valid?Return input errorsPriority AnalysisDynamic Prompt BuilderLLM APIParse JSON ResponsePython ValidationTimetable valid?Return timetableBuild correction promptFrontend displays timetableNoYesYesNo





8.4 Why Separate These Modules?
Consider what happens if you change your LLM provider.

If all your application logic is written inside app.py, changing the API integration can become difficult.

With separate modules:
- You can change the LLM without rewriting scheduling validation.
- You can improve prompts without changing frontend code.
- You can test validation independently.
- You can replace the LLM with a rule-based generator in the future.
This modularity is especially valuable for a prompt engineering project because you will likely experiment with different prompts.

9. LLM API Integration
9.1 API Communication
The backend should communicate with an LLM provider through its API.

The general interaction will be:
1. Construct the prompt.
2. Send an HTTP request to the LLM provider.
3. Receive the model response.
4. Extract the generated content.
5. Parse the JSON.
6. Validate the timetable.
You can use the provider's official Python SDK or its HTTP API.

For the initial implementation, choose one provider rather than integrating multiple providers.
9.2 API Key Management
API credentials must never be placed in frontend JavaScript.

Store them in environment variables.

For example:
LLM_API_KEY=your_api_key
LLM_MODEL=your_model_name


The .env file should not be committed to GitHub.

Use a .gitignore file to exclude it.
9.3 API Failure Handling
Your application should account for the following situations:
Failure	Recommended handling
Invalid API key	Return configuration error
Network failure	Retry a limited number of times
API rate limit	Apply backoff or ask the user to retry
API timeout	Stop the request and return an error
Empty response	Treat as generation failure
Invalid JSON	Attempt parsing recovery or regeneration
Unexpected response	Log error and return a safe response
Token limit exceeded	Reduce unnecessary prompt content or split the request

9.4 Security Requirements
- Keep API keys on the backend.
- Never expose raw API credentials to the browser.
- Limit input lengths.
- Sanitize user-provided content before displaying it.
- Do not execute generated AI content as code.
- Set request timeouts.
- Avoid logging API keys or unnecessary personal information.
9.5 LLM Provider Recommendation
For your first version, use one LLM API that supports:
- Reliable instruction following.
- JSON or structured output.
- Reasonable context limits.
- A usable Python SDK.
- Affordable testing.
The exact provider can be selected when you reach the API integration stage.

10. Frontend Requirements
The frontend should be simple, intuitive and responsive.

You do not need React or another frontend framework for the first version. HTML, CSS and JavaScript are sufficient.
10.1 Main Pages
I recommend three main interface sections.
Page 1: Student Information Form








dribbble.com


Conceptual UI reference

The student enters:
- Study availability.
- Start date.
- Subject details.
- Examination dates.
- Difficulty and preparation percentages.
- Optional preferences.
Page 2: Timetable Results








studyflow.it


Conceptual UI reference

Display:
- Date-wise schedules.
- Study sessions.
- Subject names.
- Durations.
- Breaks.
- Daily study totals.
Page 3: Timetable Summary








devpost.com


Conceptual UI reference

Display:
- Total preparation days.
- Subject-wise time allocation.
- Daily study hours.
- Revision distribution.
- Preparation overview.

10.2 Input Form Requirements
The subject section should support dynamic addition and removal.

For example:
Add Subject
Subject nameMathematics

Examination date20 November 2026

DifficultyHard

Preparation40%


Syllabus topics (optional)

Integration, Matrices...

 Add another subjectIllustrative form layout, not a functioning application.
10.3 Timetable Display
Use a table for the main timetable.

Recommended columns:
Date	Subject	Study task	Duration	Type
16 Nov	Mathematics	Integration	60 min	Learning
16 Nov	Mathematics	Problem solving	60 min	Practice
16 Nov	DBMS	SQL revision	30 min	Revision

Breaks can be displayed as separate rows or timeline elements.

Also provide:
- A daily view.
- A full timetable view.
- Subject-wise filters.
- A print-friendly layout.
10.4 Frontend-Backend Communication
Use JavaScript's Fetch API to send student information to Flask.

The backend should return JSON.

JavaScript should then dynamically render the returned timetable.

The frontend should never independently trust or modify the AI-generated schedule to make it appear valid. Only display the validated backend response.

11. Testing Requirements
Testing should cover the entire application, especially the scheduling validator.

I recommend using pytest for backend testing.
11.1 Input Validation Tests
Test case	Input condition	Expected result
IT-01	All fields valid	Accept input
IT-02	Missing subject name	Reject input
IT-03	Preparation = 120%	Reject input
IT-04	Negative study hours	Reject input
IT-05	Invalid date format	Reject input
IT-06	Examination before start date	Reject input
IT-07	Multiple valid subjects	Accept input
IT-08	Optional preferences missing	Accept input

11.2 Prompt Engineering Tests
Test case	Scenario	Expected result
PT-01	One subject	Prompt includes one subject
PT-02	Five subjects	Prompt includes all five
PT-03	Different exam dates	Correct dates injected
PT-04	Optional preferences supplied	Preferences included
PT-05	No syllabus topics	No fabricated student syllabus
PT-06	Different study hours	Prompt reflects available hours

11.3 Timetable Validation Tests
Test case	Scenario	Expected result
VT-01	Valid timetable	Pass
VT-02	Daily hours exceed limit	Fail
VT-03	Overlapping sessions	Fail
VT-04	Invalid subject name	Fail
VT-05	Negative duration	Fail
VT-06	Missing date	Fail
VT-07	Session after examination	Fail
VT-08	Break overlaps session	Fail
VT-09	Incorrect daily total	Fail
VT-10	Malformed JSON	Fail

11.4 Integration Tests
These tests check whether different modules work together.

Examples:
1. Student submits valid data.
2. Flask receives the request.
3. Prompt builder constructs the prompt.
4. Mock LLM returns a valid response.
5. Python validates the response.
6. Flask returns the final JSON.
Also test:
- LLM API timeout.
- Invalid API response.
- Regeneration after validation failure.
- Failure after maximum retries.
- Multiple simultaneous requests.
Use mocked LLM responses during most automated tests. This avoids spending API credits every time you run your test suite.
11.5 End-to-End Testing
Finally, test the complete application through the browser.

A successful end-to-end test should verify that a student can:
1. Open the application.
2. Enter academic information.
3. Add multiple subjects.
4. Submit the form.
5. Receive a generated timetable.
6. View the timetable.
7. See meaningful errors when inputs are invalid.

12. Additional Technical Recommendations
These are not essential for the first version, but they will improve the project.
12.1 Keep Generation and Validation Independent
This is probably the most important architectural decision.

Do not put all scheduling logic inside the prompt.

Your application should have two distinct responsibilities:
LLM	Python
Decide which topics to study	Verify subject validity
Decide subject prioritization	Verify examination dates
Generate study tasks	Verify study durations
Distribute revision	Verify daily hour limits
Suggest breaks	Verify time overlaps
Personalize the schedule	Verify JSON structure

This separation makes the application more reliable.
12.2 Introduce a Rule-Based Fallback Later
Eventually, you could develop a basic rule-based timetable generator.

If the LLM API becomes unavailable, the application could generate a simpler schedule using predefined scheduling rules.

This is an optional enhancement, not a requirement for the MVP.
12.3 Measure Prompt Quality
Since this is a prompt engineering project, you should evaluate more than whether the API returns JSON.

Consider measuring:
- JSON validity rate.
- Scheduling constraint satisfaction rate.
- Number of regeneration attempts.
- Subject allocation balance.
- Revision coverage.
- Average API response time.
- Token usage and generation cost.
You could compare multiple prompt versions against the same set of student inputs.

That would make your project much stronger academically because you would have measurable evidence of prompt improvement.
12.4 Database: When Should You Add It?
For the initial version, you can keep the application stateless: accept inputs, generate the timetable and return the result.

A database is only necessary when you introduce features such as:
- User accounts.
- Saved timetables.
- Timetable history.
- Editing and regenerating existing schedules.
- Tracking completed study sessions.
SQLite would be sufficient for a student-level project.

13. Minimum Viable Product (MVP)
To avoid making the project unnecessarily complicated, I recommend dividing features into two categories.
Feature	MVP	Future enhancement
Multiple subject inputs	Yes	
Examination dates	Yes	
Difficulty and preparation levels	Yes	
Available study hours	Yes	
Optional preferences	Yes	
Dynamic prompt generation	Yes	
LLM API integration	Yes	
JSON response	Yes	
Python validation	Yes	
Invalid response regeneration	Yes	
Interactive timetable display	Yes	
User authentication		Later
Database persistence		Later
Export to PDF		Later
Edit timetable manually		Later
Progress tracking		Later
Rule-based fallback		Later


14. Proposed Development Sequence
I strongly recommend developing this application incrementally.

Do not attempt to build the frontend, backend, AI integration and validation system simultaneously.

Each phase should produce a working component that can be tested before moving forward.
Development roadmap
1. Phase 1 – Input design and data modeling
   
   Define the student input structure, mandatory fields, optional preferences and JSON schemas.
   Foundation
2. Phase 2 – Scheduling logic and constraints
   
   Define how priorities are calculated, what scheduling rules apply and what constitutes an invalid timetable.
3. Phase 3 – Prompt engineering
   
   Develop the initial prompt template, inject dynamic student information and define the expected JSON output.
4. Phase 4 – LLM API integration
   
   Connect Python to the selected LLM API, send prompts and receive structured responses.
5. Phase 5 – Python validation system
   
   Implement structural validation, duration calculations, overlap detection and correction handling.
6. Phase 6 – Backend development
   
   Integrate the modules using Flask routes and establish request-response communication.
7. Phase 7 – Frontend development
   
   Build the student form, dynamic subject fields and timetable results interface.
8. Phase 8 – Integration and testing
   
   Test normal inputs, invalid inputs, API failures and conflicting scheduling constraints.
9. Phase 9 – Final improvements
   
   Improve prompt quality, add timetable summaries, polish the interface and prepare project documentation.

15. Final Architectural Summary
The recommended application architecture is:
Frontend

HTML + CSS + JavaScript

Student inputs and timetable display


Flask Backend

Request handling and application coordination


Prompt Engine

Dynamic instruction construction


Input Validator

Input checking and normalization




LLM API

Study planning and JSON generation


Python Validation Engine

Schema validation and scheduling constraint enforcement


Validated JSON Response

Returned to frontend for timetable rendering


Final recommendation: Keep the first version focused on three core capabilities: dynamic prompt engineering, LLM-based timetable generation and independent Python validation.

These three components are the actual technical foundation of your project. The frontend is the interface through which students interact with them.

The most important thing is to build and test each component independently before integrating them.

Next development step: Start with Phase 1 – Input Design and Data Modeling. The first deliverable should be a clearly defined input JSON schema and output JSON schema. Once those are finalized, the rest of the application can be developed around them.