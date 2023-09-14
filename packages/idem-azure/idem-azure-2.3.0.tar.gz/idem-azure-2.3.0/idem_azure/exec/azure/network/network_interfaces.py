"""Exec module for managing Network Interfaces"""

__func_alias__ = {"list_": "list"}

from typing import Dict
from collections import OrderedDict


RESOURCE_TYPE = "network.network_interfaces"


async def get(hub, ctx, resource_id: str, name: str = None, raw: bool = False) -> Dict:
    """Gets Network interface from azure account.

    Args:
        resource_id(str):
            The resource id of the Network interface.
        name(str, Optional):
            The name of the resource
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.network.network_interfaces.get resource_id="value" raw="False"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.network.network_interfaces.get
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkInterfaces/{network_interface_name}"
                    raw: False
    """
    result = dict(comment=[], ret=None, result=True)

    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version={api_version}",
        success_codes=[200],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"].extend(
            hub.tool.azure.result_utils.extract_error_comments(response_get)
        )
        return result
    if raw:
        result["ret"] = response_get["ret"]
    else:
        uri_parameters = OrderedDict(
            {
                "subscriptions": "subscriptionId",
                "resourceGroups": "resourceGroupName",
                "networkInterfaces": "networkInterfaceName",
            }
        )
        uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
            resource_id, uri_parameters
        )
        result[
            "ret"
        ] = hub.tool.azure.network.network_interfaces.convert_raw_to_present_state(
            {**uri_parameter_values, **response_get["ret"]}
        )

        result["ret"]["name"] = resource_id
        result["ret"]["resource_id"] = resource_id
    return result


async def list_(
    hub,
    ctx,
) -> Dict:
    """Lists all Network Interface.

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.network.network_interfaces.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.network.network_interfaces.list

    """
    result = dict(comment=[], ret=[], result=True)
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscriptionId",
            "resourceGroups": "resourceGroupName",
            "networkInterfaces": "networkInterfaceName",
        }
    )
    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/providers/Microsoft.Network/networkInterfaces?api-version={api_version}",
        success_codes=[200],
    ):
        resource_list = page_result.get("value", None)
        if resource_list:
            for resource in resource_list:
                resource_id = resource["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )
                present_state = hub.tool.azure.network.network_interfaces.convert_raw_to_present_state(
                    {**uri_parameter_values, **resource}
                )

                present_state["resource_id"] = resource_id
                present_state["name"] = resource_id

                result["ret"].append(present_state)
    return result
