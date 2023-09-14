from typing import Any
from typing import Dict
from typing import List


def cleanup_none_values(hub, input_dict: Dict):
    return {k: v for (k, v) in input_dict.items() if v is not None}


def dict_add_nested_key_value_pair(
    hub, input_dict: Dict[str, Any], key_path: List[str], value
):
    recurse_dict = input_dict
    for idx, key in enumerate(key_path):
        if idx == len(key_path) - 1:
            recurse_dict[key] = value
            break
        recurse_dict.setdefault(key, {})
        recurse_dict = recurse_dict[key]
    return input_dict
