import json
import re

def replace_empty_strings_with_none(data):
    if isinstance(data, dict):
        return {key: replace_empty_strings_with_none(value) if value != "" else None for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_empty_strings_with_none(item) for item in data]
    elif isinstance(data, str) and data == "":
        return None
    else:
        return data
    #
#

def clean_json(json_data):
    # Convertir le dictionnaire en une chaîne JSON
    json_str = json.dumps(json_data, ensure_ascii=False)

    # Rechercher et remplacer les séquences d'échappement Unicode dans la chaîne JSON
    decoded_str = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), json_str)

    # Convertir la chaîne JSON décodée en un dictionnaire
    json_data = json.loads(decoded_str)
    return replace_empty_strings_with_none(json_data)
