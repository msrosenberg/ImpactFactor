"""
functions shared by multiple modules
"""

def encode_name(name: str) -> str:
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    name = name.replace("/", "_")
    name = name.replace("(", "")
    name = name.replace(")", "")
    name = name.replace(".", "_")
    name = name.replace("%", "")
    return name
