"""Exec module for managing Compute Disks."""

__func_alias__ = {"list_": "list"}

from collections import OrderedDict
from typing import Dict, Any


async def get(
    hub, ctx, resource_id: str, name: str = None, raw: bool = False
) -> Dict[str, Any]:
    """Get compute disks resource by resource_id.

    Args:
        resource_id(str):
            The resource_id of a disk
        name(str, Optional):
            The name of the resource
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.disks.get resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.compute.disks.get
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/disks/{disk_name}"

    """
    result = dict(comment=[], result=True, ret=None)
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscriptionId",
            "resourceGroups": "resourceGroupName",
            "disks": "diskName",
        }
    )

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{hub.exec.azure.URL}{resource_id}?api-version={hub.tool.azure.api_versions.compute.disks}",
        success_codes=[200],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"].extend(
            hub.tool.azure.result_utils.extract_error_comments(response_get)
        )
        return result

    elif response_get["result"] and response_get["ret"]:
        if raw:
            result["ret"] = response_get["ret"]
        else:
            uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                resource_id, uri_parameters
            )
            result["ret"] = hub.tool.azure.compute.disks.convert_raw_to_present_state(
                {**uri_parameter_values, **response_get["ret"]}
            )

            result["ret"]["resource_id"] = resource_id

    return result


async def list_(hub, ctx) -> Dict:
    """List of compute disks.

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.disks.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.compute.disks.list


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscriptionId",
            "resourceGroups": "resourceGroupName",
            "disks": "diskName",
        }
    )
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Compute/disks?api-version={hub.tool.azure.api_versions.compute.disks}",
        success_codes=[200],
    ):
        resource_list = page_result.get("value")
        if resource_list:
            for resource_raw_state in resource_list:
                resource_id = resource_raw_state["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )
                resource_present_state = (
                    hub.tool.azure.compute.disks.convert_raw_to_present_state(
                        {**uri_parameter_values, **resource_raw_state}
                    )
                )
                resource_present_state["resource_id"] = resource_id
                resource_present_state["name"] = resource_id
                result["ret"].append(resource_present_state)

    return result
