def validate_user_input(data, required_fields):
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return False, f"Missing or empty field: {field}"
    return True, ""