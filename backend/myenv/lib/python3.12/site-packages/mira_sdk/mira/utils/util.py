def split_name(name):
    parts = name.split('/')
    if len(parts) < 2:
        raise ValueError(f"Invalid name: {name}")
    org, name = parts[0].lstrip('@'), parts[1]
    return org, name
