"""Exec module for managing Virtual Network Peerings."""

__func_alias__ = {"list_": "list"}

from typing import Dict
from collections import OrderedDict


async def get(hub, ctx, resource_id: str, name: str = None, raw: bool = False) -> Dict:
    """Gets Virtual Network Peerings from azure account.

    Args:
        resource_id(str):
            The resource id of the Virtual network.
        name(str, Optional):
            The name of the resource
        raw(bool, Optional):
            Returns raw response if True. Defaults to False


    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.network.virtual_network_peerings.get resource_id="value" raw="False"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.network.virtual_network_peerings.get
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}/virtualNetworkPeerings/{virtual_network_peering_name}"
                    raw: "False"
    """
    result = dict(comment=[], ret=None, result=True)
    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-03-01",
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
                "virtualNetworks": "virtualNetworkName",
                "virtualNetworkPeerings": "virtualNetworkPeeringName",
            }
        )
        uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
            resource_id, uri_parameters
        )
        result[
            "ret"
        ] = hub.tool.azure.network.virtual_network_peerings.convert_raw_to_present_state(
            {**uri_parameter_values, **response_get["ret"]}
        )

        result["ret"]["name"] = resource_id
        result["ret"]["resource_id"] = resource_id
    return result


async def list_(
    hub,
    ctx,
) -> Dict:
    """Lists all Virtual Network Peerings.

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.network.virtual_network_peerings.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.network.virtual_network_peerings.list

    """
    result = dict(comment=[], ret=[], result=True)
    subscription_id = ctx.acct.subscription_id

    virtual_networks_list = await hub.exec.azure.network.virtual_networks.list(ctx)
    if not virtual_networks_list["result"]:
        result["result"] = False
        result["comment"].append(virtual_networks_list["comment"])
        return result

    for vn in virtual_networks_list["ret"]:
        vn_name = vn["virtual_network_name"]
        resource_group_name = vn["resource_group_name"]
        uri_parameters = OrderedDict(
            {
                "subscriptions": "subscriptionId",
                "resourceGroups": "resourceGroupName",
                "virtualNetworks": "virtualNetworkName",
                "virtualNetworkPeerings": "virtualNetworkPeeringName",
            }
        )
        async for page_result in hub.tool.azure.request.paginate(
            ctx,
            url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{vn_name}/virtualNetworkPeerings?api-version=2021-03-01",
            success_codes=[200, 404],
        ):
            resource_list = page_result.get("value", None)
            if resource_list:
                for resource_raw_state in resource_list:
                    resource_id = resource_raw_state["id"]
                    uri_parameter_values = (
                        hub.tool.azure.uri.get_parameter_value_in_dict(
                            resource_id, uri_parameters
                        )
                    )
                    resource_present_state = hub.tool.azure.network.virtual_network_peerings.convert_raw_to_present_state(
                        {**uri_parameter_values, **resource_raw_state}
                    )
                    resource_present_state["resource_id"] = resource_id
                    resource_present_state["name"] = resource_id

                    result["ret"].append(resource_present_state)

    return result
