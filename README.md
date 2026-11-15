# 📚 AI-Powered Timetable & Study Plan Generator

An AI-powered study planning system that generates personalized, day-wise study timetables based on students' subjects, examination dates, available study hours and preparation requirements.

The project explores **Prompt Engineering** techniques to generate structured, realistic and constraint-aware study plans using different AI models.

## 🎯 Problem Statement

Students often struggle to create effective study schedules when preparing for multiple examinations simultaneously.

Manually planning a timetable involves considering several factors:
- Number of subjects to prepare.
- Examination dates and the order of exams.
- Available study hours per day.
- Subject difficulty and preparation requirements.
- Time required for revision and practice.
- Breaks and realistic daily workloads.

Generic study schedules often fail to account for these individual constraints. As a result, students may end up with unrealistic timetables, insufficient revision time or uneven distribution of subjects.

**Objective:** Develop an AI-based timetable generator that converts students' study requirements into a personalized, practical and well-structured day-wise study plan.

## 💡 Proposed Solution

The system will accept student-specific inputs, process them through carefully designed prompts and generate a customized study timetable.

### Input Parameters

| Parameter | Description |
|---|---|
| Subjects | List of subjects to prepare |
| Exam Dates | Examination dates for each subject |
| Free Hours | Available study hours per day |
| Difficulty Level | Relative difficulty of each subject |
| Preparation Status | Current preparation level |
| Study Preferences | Preferred study timings or other requirements |

### Expected Output

The AI should generate a structured timetable in tabular format containing:

- Date and day.
- Subject to study.
- Specific topics or study tasks.
- Allocated study duration.
- Revision and practice sessions.
- Breaks and buffer time.

The generated plan should respect the student's available hours and examination deadlines.

## ⚙️ Initial Technical Approach

The project primarily focuses on **Prompt Engineering and evaluating the responses of different AI models** rather than developing a machine learning model from scratch.

The initial approach involves the following stages:

### 1. Requirement and Constraint Identification

Identify the parameters that influence timetable generation and convert them into explicit constraints.

Examples:
- Daily study hours must not exceed the student's available time.
- Every subject must receive adequate preparation time.
- Subjects with earlier examination dates should receive appropriate priority.
- Revision sessions should be scheduled before examinations.
- Breaks should be included to avoid unrealistic study schedules.

### 2. Prompt Design

Develop structured prompts that clearly communicate the student's requirements, constraints and expected output.

Prompt engineering techniques to explore:

- **Role-based prompting:** Assigning the AI the role of an academic planner or study mentor.
- **Constraint-based prompting:** Explicitly defining time limits, examination deadlines and scheduling rules.
- **Contextual prompting:** Providing subject difficulty, preparation status and student preferences.
- **Structured output prompting:** Requiring the AI to return results in a predefined tabular or JSON format.
- **Iterative prompting:** Refining prompts based on the quality and accuracy of generated timetables.

### 3. Experimentation Across AI Models

Test the same or equivalent prompts across different AI models to evaluate their timetable-generation capabilities.

The objective is to understand how different models interpret constraints, distribute study hours and handle complex scheduling requirements.

### 4. Output Generation

Generate a day-wise timetable in a structured format.

The output should be easy to read, interpret and potentially convert into a table in a user interface.

### 5. Constraint Checking and Validation

Evaluate the generated timetable against the original input requirements.

Validation will initially focus on:
- Total allocated study hours per day.
- Coverage of all specified subjects.
- Examination deadline compliance.
- Revision scheduling.
- Conflicting or overlapping study sessions.
- Missing dates or unallocated time.

If the generated timetable violates important constraints, the system can use feedback-based prompting to request corrections from the AI.

## 🧪 Prompt Engineering Techniques Under Exploration

| Technique | Purpose |
|---|---|
| Role-based prompting | Establish the AI's planning role |
| Constraint-based prompting | Enforce scheduling requirements |
| Few-shot prompting | Demonstrate examples of desired timetables |
| Structured output prompting | Generate consistent tables or JSON |
| Iterative refinement | Improve outputs through feedback |
| Comparative prompting | Evaluate responses from different AI models |

## 🛠️ Initial Technology Considerations

The technology stack will be finalized as experimentation progresses.

- **AI Models:** Different LLMs for prompt experimentation and comparison.
- **Prompt Design:** Natural language instructions and structured prompt templates.
- **Output Format:** Markdown tables / JSON.
- **Validation:** Python-based constraint checking.
- **Development Environment:** Python, VS Code and Jupyter Notebook.

## 📊 Evaluation Criteria

The generated timetables will be evaluated based on:

1. **Constraint Satisfaction:** Does the timetable follow all specified requirements?
2. **Time Allocation:** Are study hours distributed appropriately?
3. **Subject Coverage:** Are all subjects adequately included?
4. **Deadline Awareness:** Does the plan prioritize upcoming examinations?
5. **Output Consistency:** Is the response structured and easy to understand?
6. **Model Comparison:** Which AI model produces the most reliable results?

## 🚀 Project Goal

The ultimate goal is to explore how effective prompt engineering can transform general-purpose AI models into practical academic planning assistants.

The project will demonstrate how prompt structure, explicit constraints, output formatting and validation can improve the reliability and usefulness of AI-generated results.

---

**Project Status:** Initial Planning & Prompt Experimentation