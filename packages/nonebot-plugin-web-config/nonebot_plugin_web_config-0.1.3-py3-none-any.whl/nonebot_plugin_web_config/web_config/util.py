import ast
import json
from typing import Union


def decode_json(obj: Union[str, dict]):
    if isinstance(obj, str):
        obj = json.loads(obj)

    for key, value in obj.items():
        try:
            obj[key] = ast.literal_eval(value)
        except Exception:
            try:
                obj[key] = json.loads(value)
            except Exception:
                pass

    return obj
