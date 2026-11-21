import json

from app.models.output_models import TimetableOutput

schema = TimetableOutput.model_json_schema()

print(json.dumps(schema, indent=2))