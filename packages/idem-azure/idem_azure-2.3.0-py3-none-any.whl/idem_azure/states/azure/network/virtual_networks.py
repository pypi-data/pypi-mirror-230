"""State module for managing Virtual Network."""
import copy
from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List


__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    virtual_network_name: str,
    address_space: List[str],
    location: str,
    resource_id: str = None,
    extended_location: make_dataclass(
        "ExtendedLocation",
        [
            ("name", str),
            ("type", str),
        ],
    ) = None,
    bgp_communities: make_dataclass(
        "VirtualNetworkBgpCommunities",
        [
            ("virtual_network_community", str),
        ],
    ) = None,
    flow_timeout_in_minutes: int = None,
    subnets: List[
        make_dataclass(
            "SubnetSet",
            [
                ("name", str, field(default=None)),
                ("address_prefix", str, field(default=None)),
                ("address_prefixes", List, field(default=None)),
                ("security_group_id", str, field(default=None)),
                ("service_endpoints", List, field(default=None)),
            ],
        )
    ] = None,
    ddos_protection_plan: make_dataclass(
        "Id",
        [
            ("id", str),
        ],
    ) = None,
    enable_ddos_protection: bool = None,
    enable_vm_protection: bool = None,
    dhcp_options: make_dataclass(
        "DhcpOptions", [("dns_servers", List[str], field(default=None))]
    ) = None,
    subscription_id: str = None,
    tags: Dict = None,
) -> Dict:
    r"""Create or update Virtual Networks.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        virtual_network_name(str): The name of the virtual network.
        address_space(list): An array of IP address ranges that can be used by subnets of the virtual network.
        location(str): Resource location. This field can not be updated.
        resource_id(str, Optional): Virtual Network resource id on Azure.
        extended_location(Dict, Optional): The extended location of the virtual network.

            * name(str):
                The name of the extended location.
            * type(str):
                The type of the extended location.
                Enum type. Allowed values: EdgeZone
        bgp_communities(Dict, Optional): Bgp Communities sent over ExpressRoute with each route corresponding to a prefix in this VNET.

            * virtual_network_community(str):
                The BGP community associated with the virtual network.
        flow_timeout_in_minutes(int, Optional): The FlowTimeout value (in minutes) for the Virtual Network
        subnets(list, Optional): List of Subnet in a virtual network resource.Each Subnet will have fields

            * name(str, Optional):
                The name of subnet.
            * address_prefix(str, Optional):
                The address prefix for the subnet.
            * address_prefixes(list, Optional):
                List of address prefixes for the subnet.
            * security_group_id(str, Optional):
                The security group id.
            * service_endpoints(list, Optional):
                List of service endpoint.
        dhcp_options(Dict, Optional): DhcpOptions contains an array of DNS servers available to VMs deployed in the virtual network. Standard DHCP option for a subnet overrides VNET DHCP options.

            * dns_servers(List, Optional):
                The list of DNS servers IP addresses.
        ddos_protection_plan(Dict, Optional):

            * id(str):
                The DDoS protection plan associated with the virtual network.
        enable_ddos_protection(bool, Optional): Indicates if DDoS protection is enabled for all the protected resources in the virtual network. It requires a DDoS protection plan associated with the resource.
        enable_vm_protection(bool, Optional): Indicates if VM protection is enabled for all the subnets in the virtual network.
        subscription_id(str, Optional): Subscription Unique id.
        tags(dict, Optional): Resource tags.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            my-vnet:
              azure.network.virtual_networks.present:
                - name: my-vnet
                - resource_group_name: my-rg-1
                - virtual_network_name: my-vnet-1
                - location: westus
                - flow_timeout_in_minutes: 15
                - tags:
                    my-tag-key: my-tag-value
                - subnets:
                    - name: subnet_name
                      address_prefix: 10.0.0.0/26
                      security_group_id: /subscriptions/subscription_id/resourceGroups/resource_group_name/providers/Microsoft.Network/networkSecurityGroups/network-security-group-name
                      service_endpoints:
                          - Microsoft.Storage
                - address_space:
                    - 10.0.0.0/26
    """
    result = ctx.get("wrapper_result")

    if ctx.get("skip_present"):
        return result

    if not result:
        error_message = hub.tool.azure.comment_utils.no_result_from_wrapper(
            "azure.network.virtual_networks", name
        )
        hub.log.error(error_message)
        return {
            "result": False,
            "old_state": None,
            "new_state": None,
            "name": name,
            "comment": [error_message],
        }

    computed = ctx.get("computed")
    computed_resource_id = computed.get("resource_id")
    computed_resource_url = computed.get("resource_url")
    existing_resource = result["old_state"]

    if not existing_resource:
        if ctx.get("test", False):
            # Return a proposed state by Idem state --test
            result["new_state"] = hub.tool.azure.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "resource_group_name": resource_group_name,
                    "virtual_network_name": virtual_network_name,
                    "address_space": address_space,
                    "tags": tags,
                    "location": location,
                    "resource_id": computed_resource_id,
                    "extended_location": extended_location,
                    "flow_timeout_in_minutes": flow_timeout_in_minutes,
                    "bgp_communities": bgp_communities,
                    "subnets": subnets,
                    "ddos_protection_plan": ddos_protection_plan,
                    "enable_ddos_protection": enable_ddos_protection,
                    "enable_vm_protection": enable_vm_protection,
                    "dhcp_options": dhcp_options,
                    "subscription_id": subscription_id,
                },
            )
            result["comment"].append(
                f"Would create azure.network.virtual_networks '{name}'"
            )
            return result
        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.network.virtual_networks.convert_present_to_raw_virtual_network(
                subscription_id=subscription_id,
                address_space=address_space,
                location=location,
                extended_location=extended_location,
                bgp_communities=bgp_communities,
                flow_timeout_in_minutes=flow_timeout_in_minutes,
                subnets=subnets,
                ddos_protection_plan=ddos_protection_plan,
                enable_ddos_protection=enable_ddos_protection,
                enable_vm_protection=enable_vm_protection,
                dhcp_options=dhcp_options,
                tags=tags,
            )
            response_put = await hub.exec.request.json.put(
                ctx,
                url=computed_resource_url,
                success_codes=[200, 201],
                json=payload,
            )

            if not response_put["result"]:
                hub.log.debug(
                    f"Could not create azure.network.virtual_networks {response_put['comment']} {response_put['ret']}"
                )
                result["comment"].extend(
                    hub.tool.azure.result_utils.extract_error_comments(response_put)
                )
                result["result"] = False
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.virtual_networks.convert_raw_virtual_network_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                virtual_network_name=virtual_network_name,
                resource_id=computed_resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(f"Created azure.network.virtual_networks '{name}'")
            return result

    else:
        raw_existing_resource = hub.tool.azure.network.virtual_networks.convert_present_to_raw_virtual_network(
            **existing_resource
        )
        # Generate a new PUT operation payload with new values
        new_payload = (
            hub.tool.azure.network.virtual_networks.update_virtual_network_payload(
                subscription_id,
                raw_existing_resource,
                {
                    "extended_location": extended_location,
                    "address_space": address_space,
                    "bgp_communities": bgp_communities,
                    "flow_timeout_in_minutes": flow_timeout_in_minutes,
                    "subnets": subnets,
                    "ddos_protection_plan": ddos_protection_plan,
                    "enable_ddos_protection": enable_ddos_protection,
                    "enable_vm_protection": enable_vm_protection,
                    "dhcp_options": dhcp_options,
                    "tags": tags,
                },
            )
        )
        if ctx.get("test", False):
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    hub.tool.azure.comment_utils.no_property_to_be_updated_comment(
                        "azure.network.virtual_networks", name
                    )
                )
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.network.virtual_networks.convert_raw_virtual_network_to_present(
                    resource=new_payload["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    virtual_network_name=virtual_network_name,
                    resource_id=computed_resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(
                    f"Would update azure.network.virtual_networks '{name}'"
                )
            return result
        # PUT operation to update a resource
        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                hub.tool.azure.comment_utils.no_property_to_be_updated_comment(
                    "azure.network.virtual_networks", name
                )
            )
            return result
        result["comment"].extend(new_payload["comment"])
        response_put = await hub.exec.request.json.put(
            ctx,
            url=computed_resource_url,
            success_codes=[200],
            json=new_payload["ret"],
        )

        if not response_put["result"]:
            hub.log.debug(
                f"Could not update azure.network.virtual_networks {response_put['comment']} {response_put['ret']}"
            )
            result["result"] = False
            result["comment"].extend(
                hub.tool.azure.result_utils.extract_error_comments(response_put)
            )
            return result

        result[
            "new_state"
        ] = hub.tool.azure.network.virtual_networks.convert_raw_virtual_network_to_present(
            resource=response_put["ret"],
            idem_resource_name=name,
            resource_group_name=resource_group_name,
            virtual_network_name=virtual_network_name,
            resource_id=computed_resource_id,
            subscription_id=subscription_id,
        )
        result["comment"].append(f"Updated azure.network.virtual_networks '{name}'")
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    resource_group_name: str = None,
    virtual_network_name: str = None,
    subscription_id: str = None,
) -> Dict:
    r"""Delete Virtual Networks.

    Args:
        name(str): The identifier for this state.
        resource_id(str, Optional): Virtual Network resource id on Azure.
        resource_group_name(str, Optional): The name of the resource group.
        virtual_network_name(str, Optional): The name of the virtual network.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.virtual_networks.absent:
                - name: value
                - resource_group_name: value
                - virtual_network_name: value
    """
    # Resource deletion is handled via common recursive_contracts.init#call_absent() wrapper
    raise NotImplementedError


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Virtual Networks under the same subscription

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.virtual_networks
    """
    result = {}
    ret_list = await hub.exec.azure.network.virtual_networks.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe network virtual_networks {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.virtual_networks.present": [
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
