
import json
import urllib.request
import urllib.error


student_data = {
    "start_date": "2026-11-16",
    "max_daily_hours": 4,
    "subjects": [
        {
            "name": "Mathematics",
            "exam_date": "2026-11-20",
            "difficulty": "hard",
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
            "difficulty": "medium",
            "preparation_percentage": 60,
            "topics": [
                "Normalization",
                "SQL",
                "Transactions"
            ]
        }
    ],
    "preferences": {
        "max_session_duration_minutes": 90
    }
}


url = "http://127.0.0.1:5000/api/generate-timetable"

request = urllib.request.Request(
    url,
    data=json.dumps(student_data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(request, timeout=180) as response:

        result = json.loads(response.read().decode("utf-8"))

        print("\nStatus:", response.status)
        print("\nGenerated Timetable:\n")
        print(json.dumps(result, indent=4))

except urllib.error.HTTPError as error:

    print("\nHTTP Error:", error.code)
    print(error.read().decode("utf-8"))

except Exception as error:

    print("\nRequest failed:", str(error))
