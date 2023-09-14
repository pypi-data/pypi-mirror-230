"""State module for managing Network interface."""
from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List


__contracts__ = ["resource"]
RESOURCE_TYPE = "network.network_interfaces"


async def present(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    network_interface_name: str,
    location: str,
    ip_configurations: List[
        make_dataclass(
            "IpConfigurationsSet",
            [
                ("name", str, field(default=None)),
                ("private_ip_address_allocation", str, field(default=None)),
                ("subnet_id", str, field(default=None)),
                ("private_ip_address_version", str, field(default=None)),
                ("private_ip_address", str, field(default=None)),
                ("public_ip_address_id", str, field(default=None)),
                ("primary", bool, field(default=False)),
            ],
        )
    ],
    enable_accelerated_networking: bool = None,
    dns_settings: make_dataclass(
        "NetworkInterfaceDnsSettings",
        [
            ("dns_servers", List[str], field(default=None)),
            ("internal_dns_name_label", str, field(default=None)),
        ],
    ) = None,
    network_security_group_id: str = None,
    tags: Dict = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Network Interfaces.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        network_interface_name(str): The name of the network interface.
        location(str): Resource location. This field can not be updated.
        ip_configurations(List[Dict[str, Any]]): A list of IPConfigurations of the network interface. Each ip configuration supports fields:

            * name(str):
                The name of the resource that is unique within a resource group.
            * private_ip_address_allocation(str):
                The allocation method used for the Private IP Address. Possible values are Dynamic and Static.
                Azure does not assign a Dynamic IP Address until the Network Interface is attached to a running Virtual Machine(or other resource).
            * subnet_id(str):
                Resource ID of the Subnet bound to the IP configuration. The name of the resource that is unique within a resource group.
                This is required when private_ip_address_version is set to IPv4.
            * private_ip_address_version(str):
                The specific IP configuration is IPv4 or IPv6. Default is IPv4.
            * private_ip_address(str):
                The Static IP Address which should be used. When private_ip_address_allocation is set to Static, private_ip_address can be configured.
            * public_ip_address_id(str):
                Resource ID of the Public IP address bound to the IP configuration. The name of the resource that is unique within a resource group.
            * primary(bool):
                To check if this is the primary IP Configuration. Must be true for the first ip_configuration when
                multiple are specified. Defaults to false. Primary attribute must be true for the first ip_configuration
                when multiple are specified. Defaults to false.
        enable_accelerated_networking(bool, Optional): If the network interface is accelerated networking enabled.
        dns_settings(Dict[str, Any], Optional): The DNS settings in network interface.

            * dns_servers(List[str, Any], Optional):
                List of DNS servers IP addresses. Use 'AzureProvidedDNS' to switch to azure provided DNS resolution. 'AzureProvidedDNS' value cannot be combined with other IPs, it must be the only value in dnsServers collection.
            * internal_dns_name_label(str, Optional):
                Relative DNS name for this NIC used for internal communications between VMs in the same virtual network.

        network_security_group_id(str, Optional): ID of the network security group.
        tags(Dict[str, str], Optional): Resource tags.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Network Interface resource id on Azure.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            my-nic:
              azure.network.network_interfaces.present:
                - name: my-nic
                - resource_group_name: my-rg
                - network_interface_name: my-nic
                - location: southindia
                - subscription_id: my-subscription
                - ip_configurations:
                  - name: my-ipc
                    private_ip_address_allocation: Static
                    subnet_id: subnet_name
                    private_ip_address_version: IPv4
                    private_ip_address: 10.0.0.24
                    primary: true
                - tags:
                    my-tag-key: my-tag-value

    """
    path_properties = {
        "subscription_id": subscription_id,
        "resource_group_name": resource_group_name,
        "network_interface_name": network_interface_name,
    }
    query_properties = {}
    body_properties = {
        "location": location,
        "ip_configurations": ip_configurations,
        "tags": tags,
        "enable_accelerated_networking": enable_accelerated_networking,
        "dns_settings": dns_settings,
        "network_security_group_id": network_security_group_id,
    }
    result = await hub.tool.azure.generic.run_present(
        ctx,
        "azure.network.network_interfaces",
        name,
        resource_id,
        path_properties,
        query_properties,
        body_properties,
    )

    return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    resource_group_name: str = None,
    network_interface_name: str = None,
    subscription_id: str = None,
) -> Dict:
    r"""Delete Network Interfaces.

    Args:
        name(str): The identifier for this state.
        resource_id(str, Optional): Network Interface resource id in Azure.
        resource_group_name(str): The name of the resource group.
        network_interface_name(str): The name of the network interface.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.network_interfaces.absent:
                - name: value
                - resource_group_name: value
                - network_interface_name: value
                - subscription_id: my-subscription
    """
    return hub.tool.azure.result_utils.absent_implemented_through_wrapper_result(
        "azure.network.network_interfaces", name
    )


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Network Interfaces under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.network_interfaces
    """
    result = {}
    ret_list = await hub.exec.azure.network.network_interfaces.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe network_interfaces {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.network_interfaces.present": [
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
