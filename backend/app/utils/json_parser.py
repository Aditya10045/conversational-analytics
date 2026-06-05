import json


def extract_json_object(text: str) -> dict:
    """
    Best-effort extractor for strict JSON responses.
    """
    candidate = text.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response did not contain a JSON object.")

    clipped = candidate[start : end + 1]
    return json.loads(clipped)
