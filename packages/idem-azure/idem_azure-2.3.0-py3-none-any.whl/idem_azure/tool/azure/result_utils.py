from typing import Any
from typing import Dict


def update_result_for_unsuccessful_operation(
    hub,
    result: Dict[str, Any],
    resource_type: str,
    name: str,
    response: Dict[str, Any],
    operation: str,
):
    result["result"] = False
    result["comment"].append(
        hub.tool.azure.comment_utils.could_not_do_operation_comment(
            resource_type, name, operation
        )
    )

    if response.get("comment"):
        comment = response["comment"]
        if isinstance(comment, str):
            result["comment"].append(comment)
        elif isinstance(comment, list):
            result["comment"].extend(comment)

    if response.get("ret"):
        result["comment"].append(str(response["ret"]))

    hub.log.debug(f"{result['comment']}")
    return result


def absent_implemented_through_wrapper_result(hub, resource_type: str, name: str):
    return {
        "comment": [
            f"Invalid invocation! Absent method for {resource_type} is implemented by wrapper."
        ],
        "old_state": None,
        "new_state": None,
        "name": name,
        "result": False,
    }


def extract_error_comments(hub, response: Dict[str, Any]):
    comment = []
    if response.get("comment"):
        comment.append(response["comment"])
    if isinstance(response.get("ret"), str):
        comment.append(response["ret"])

    return comment
