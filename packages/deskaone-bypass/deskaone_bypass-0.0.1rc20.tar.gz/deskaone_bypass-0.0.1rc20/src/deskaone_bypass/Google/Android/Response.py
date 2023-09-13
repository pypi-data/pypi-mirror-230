from typing import Dict


def parse_auth_response(text: str) -> Dict[str, str]:
    """Parse received auth response."""
    response_data = {}
    for line in text.split("\n"):
        if not line:
            continue

        key, _, val = line.partition("=")
        response_data[key] = val

    return response_data