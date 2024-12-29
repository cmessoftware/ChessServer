def is_null_or_empty(value):
    return value is None or value == "" or (hasattr(value, '__len__') and len(value) == 0)
