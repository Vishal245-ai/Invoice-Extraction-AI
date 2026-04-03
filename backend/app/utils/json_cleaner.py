import json
import re


def clean_json(data):
    try:
        # ✅ CASE 1: Already dict → return directly
        if isinstance(data, dict):
            return data

        # ✅ CASE 2: String → clean + parse
        if isinstance(data, str):
            data = re.sub(r"```json|```", "", data).strip()

            match = re.search(r"\{.*\}", data, re.DOTALL)
            if match:
                data = match.group(0)

            return json.loads(data)

        # ❌ Unknown type
        raise ValueError("Unsupported data format from Gemini")

    except Exception as e:
        raise ValueError(f"Invalid JSON: {str(e)}")