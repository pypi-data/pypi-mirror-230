"""State module for managing Virtual Network Peerings."""
from dataclasses import make_dataclass
from typing import Any
from typing import Dict


__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    resource_group_name: str = None,
    virtual_network_name: str = None,
    virtual_network_peering_name: str = None,
    sync_remote_address_space: bool = None,
    allow_virtual_network_access: bool = None,
    allow_forwarded_traffic: bool = None,
    allow_gateway_transit: bool = None,
    use_remote_gateways: bool = None,
    remote_virtual_network: make_dataclass(
        "Id",
        [
            ("id", str),
        ],
    ) = None,
    do_not_verify_remote_gateways: bool = None,
    subscription_id: str = None,
) -> Dict[str, Any]:
    r"""Create or update Virtual Network Peerings.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str, Optional): The name of the resource group.
        virtual_network_name(str, Optional): The name of the virtual network.
        virtual_network_peering_name(str, Optional): The name of the peering.
        sync_remote_address_space(bool, Optional): Parameter indicates the intention to sync the peering with the current address space on the remote vNet after it's updated.
        resource_id(str, Optional): Virtual Network resource id on Azure.
        allow_virtual_network_access(bool, Optional):
            Whether the VMs in the local virtual network space would be able to access the VMs in remote virtual network space.
        allow_forwarded_traffic(bool, Optional):
            Whether the forwarded traffic from the VMs in the local virtual network will be allowed/disallowed in remote virtual network.
        allow_gateway_transit(bool, Optional):
            If gateway links can be used in remote virtual networking to link to this virtual network.
        use_remote_gateways(bool, Optional):
            If remote gateways can be used on this virtual network. If the flag is set to true, and allowGatewayTransit on remote peering is also true, virtual network will use gateways of remote virtual network for transit. Only one peering can have this flag set to true. This flag cannot be set if virtual network already has a gateway.
        remote_virtual_network(Dict):

            * id(str):
                The reference to the remote virtual network. The remote virtual network can be in the same or different region (preview). See here to register for the preview and learn more (https://docs.microsoft.com/en-us/azure/virtual-network/virtual-network-create-peering).
        do_not_verify_remote_gateways(bool, Optional):
            If we need to verify the provisioning state of the remote gateway.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: sls

            my-vnet-peerings:
              azure.network.virtual_network_peerings.present:
                - virtual_network_name: network-1
                - resource_group_name: resource-group-name
                - virtual_network_peering_name: test-peering1
                - remote_virtual_network:
                    id: /subscriptions/sub-id/resourceGroups/resource-group-name/providers/Microsoft.Network/virtualNetworks/network-2
                - use_remote_gateways: False
                - allow_virtual_network_access: False
    """
    path_properties = {
        "subscription_id": subscription_id,
        "resource_group_name": resource_group_name,
        "virtual_network_name": virtual_network_name,
        "virtual_network_peering_name": virtual_network_peering_name,
    }
    query_properties = {"sync_remote_address_space": sync_remote_address_space}
    body_properties = {
        "allow_virtual_network_access": allow_virtual_network_access,
        "allow_forwarded_traffic": allow_forwarded_traffic,
        "allow_gateway_transit": allow_gateway_transit,
        "use_remote_gateways": use_remote_gateways,
        "remote_virtual_network": remote_virtual_network,
        "do_not_verify_remote_gateways": do_not_verify_remote_gateways,
    }
    return await hub.tool.azure.generic.run_present(
        ctx,
        "azure.network.virtual_network_peerings",
        name,
        resource_id,
        path_properties,
        query_properties,
        body_properties,
    )


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    resource_group_name: str = None,
    virtual_network_name: str = None,
    virtual_network_peering_name: str = None,
    subscription_id: str = None,
) -> Dict[str, Any]:
    r"""Delete Virtual Network Peerings.

    Args:
        name(str): The identifier for this state.
        resource_id(str, Optional): Virtual Network resource id on Azure.
        resource_group_name(str): The name of the resource group.
        virtual_network_name(str): The name of the virtual network.
        virtual_network_peering_name(str): The name of the virtual network peering.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.virtual_network_peerings.absent:
                - resource_group_name: value
                - virtual_network_name: value
                - virtual_network_peering_name: value

    """
    return hub.tool.azure.result_utils.absent_implemented_through_wrapper_result(
        "azure.network.virtual_network_peerings", name
    )


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Virtual Network Peerings under the same subscription

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.virtual_network_peerings
    """
    result = {}
    ret_list = await hub.exec.azure.network.virtual_network_peerings.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe network virtual_network_peerings {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.virtual_network_peerings.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result


def is_pending(hub, ret: dict, state: str = None, **pending_kwargs) -> bool:
    """Default implemented for each module."""
    return hub.tool.azure.resource_utils.is_pending(
        ret=ret, state=state, **pending_kwargs
    )
