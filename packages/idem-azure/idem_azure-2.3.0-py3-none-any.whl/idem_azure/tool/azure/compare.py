from typing import Any
from typing import Dict
from typing import List

from deepdiff import DeepDiff
from dict_tools.data import NamespaceDict
from dict_tools.differ import deep_diff


def compare_exact_matches(
    hub,
    # actual
    old_state: Dict[str, Any],
    # expected
    plan_state: Dict[str, Any],
) -> bool:
    for new_prop_name, new_prop_value in plan_state.items():
        if new_prop_value is not None and deep_diff(
            {new_prop_name: old_state.get(new_prop_name)},
            {new_prop_name: new_prop_value},
        ):
            return True
    return False


def compare_ignoring_removed_nested_items(
    hub,
    # actual
    old_state: Dict[str, Any],
    # expected
    plan_state: Dict[str, Any],
    additional_exclude_paths: List[str] = None,
) -> Dict:
    exclude_paths = additional_exclude_paths if additional_exclude_paths else []

    if (old_state is None or plan_state is None) and old_state != plan_state:
        return DeepDiff(
            old_state,
            plan_state,
            exclude_regex_paths=exclude_paths,
            ignore_type_in_groups=[(NamespaceDict, dict)],
        )

    for key in old_state.keys():
        if key not in plan_state:
            exclude_paths.append(f"root['{key}']")

    changes = DeepDiff(
        old_state,
        plan_state,
        exclude_regex_paths=exclude_paths,
        ignore_type_in_groups=[(NamespaceDict, dict)],
    )

    # If an item is in old_state but not in plan_state, i.e. changes.get("dictionary_item_removed") is not None,
    # we can ignore this change
    # type_changes can occur when a value was previously None (NoneType) and then a value was specified
    relevant_changes = (
        set(changes.get("dictionary_item_added") or set())
        | set(changes.get("iterable_item_added") or set())
        | set(changes.get("iterable_item_removed") or set())
        | set(changes.get("values_changed") or set())
        | set(changes.get("type_changes") or set())
    )

    if not relevant_changes:
        return {}

    changes["relevant_changes"] = relevant_changes
    return changes
