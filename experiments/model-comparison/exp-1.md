
# Experiment 01: Basic Prompt Comparison

## Objective
Evaluate how ChatGPT and Claude generate study timetables using a basic prompt without advanced constraint instructions.

## Models Tested
- ChatGPT
- Claude

## Input
- Mathematics: Exam 20 November, Hard, 40% prepared
- DBMS: Exam 22 November, Medium, 60% prepared
- Operating Systems: Exam 25 November, Hard, 30% prepared
- Available study time: 4 hours/day
- Preparation period: 16–25 November 2026

## Evaluation Results

| Criteria | ChatGPT | Claude |
|---|---:|---:|
| Daily time-limit compliance | 9/10 | 8/10 |
| Subject coverage | 9/10 | 9/10 |
| Exam deadline awareness | 8/10 | 9/10 |
| Revision planning | 9/10 | 9/10 |
| Realistic scheduling | 7/10 | 8/10 |
| Output structure | 9/10 | 9/10 |
| Total | 51/60 | 52/60 |

## Observations

### ChatGPT
- Distributed study sessions across all subjects.
- Included revision and mock tests.
- Claimed 40 total hours, but actual allocations sum to 38 hours.
- Provided detailed study activities.

### Claude
- Prioritized subjects according to examination dates.
- Included specific topics and revision sessions.
- Claimed 37 total hours, matching its allocations.
- Explicitly considered examination days.

## Problems Identified
1. Total study hours should be calculated and verified.
2. Examination-day scheduling assumptions should be explicit.
3. Generated timetables need independent constraint validation.

## Conclusion

Claude performed slightly better in this baseline experiment.

Both models generated useful study plans, but neither was explicitly instructed to verify all scheduling calculations.

These observations will guide subsequent prompt engineering experiments.

## Next Experiment
Role-based prompting.
