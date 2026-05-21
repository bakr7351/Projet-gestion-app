def required_fields(data, fields):
    for field in fields:
        if field not in data or data[field] == "":
            return False
    return True