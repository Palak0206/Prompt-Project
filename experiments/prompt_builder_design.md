# Prompt Builder — Initial Design

## Objective
Create a dynamic prompt from validated student input for the AI timetable generator.

## Implementation
- Accepts a validated `StudentInput` Pydantic model.
- Converts the model into JSON-compatible data.
- Inserts student information into a structured prompt.
- Defines timetable scheduling constraints.
- Specifies the expected JSON output structure.

## Design decisions
- Student information is dynamically inserted.
- Python remains responsible for independent validation.
- The LLM is instructed not to invent subjects or syllabus topics.
- The LLM must return JSON without additional explanatory text.
- Prompt generation and LLM API communication are separate responsibilities.

## Current status
Initial prompt builder implemented. Automated tests cover student information and output requirements.