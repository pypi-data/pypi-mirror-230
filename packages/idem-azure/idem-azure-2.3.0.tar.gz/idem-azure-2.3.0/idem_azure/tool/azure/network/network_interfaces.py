PRESENT_TO_RAW_MAP = {
    "subscriptionId": "subscription_id",
    "resourceGroupName": "resource_group_name",
    "networkInterfaceName": "network_interface_name",
    "tags": "tags",
    "location": "location",
    "properties": {
        "ipConfigurations": [
            {
                "$list_refs": ["ip_configurations"],
                "name": "ip_configurations.name",
                "properties": {
                    "privateIPAllocationMethod": "ip_configurations.private_ip_address_allocation",
                    "subnet": {"id": "ip_configurations.subnet_id"},
                    "privateIPAddressVersion": "ip_configurations.private_ip_address_version",
                    "privateIPAddress": "ip_configurations.private_ip_address",
                    "publicIPAddress": {"id": "ip_configurations.public_ip_address_id"},
                    "primary": "ip_configurations.primary",
                },
            }
        ],
        "enableAcceleratedNetworking": "enable_accelerated_networking",
        "dnsSettings": {
            "dnsServers": "dns_settings.dns_servers",
            "internalDnsNameLabel": "dns_settings.internal_dns_name_label",
        },
        "networkSecurityGroup": {
            "id": "network_security_group_id",
        },
    },
}


RAW_TO_PRESENT_MAP = {
    "subscription_id": "subscriptionId",
    "resource_group_name": "resourceGroupName",
    "network_interface_name": "networkInterfaceName",
    "tags": "tags",
    "location": "location",
    "ip_configurations": [
        {
            "$list_refs": ["properties.ipConfigurations"],
            "name": "properties.ipConfigurations.name",
            "private_ip_address_allocation": "properties.ipConfigurations.properties.privateIPAllocationMethod",
            "subnet_id": "properties.ipConfigurations.properties.subnet.id",
            "private_ip_address_version": "properties.ipConfigurations.properties.privateIPAddressVersion",
            "private_ip_address": "properties.ipConfigurations.properties.privateIPAddress",
            "public_ip_address_id": "properties.ipConfigurations.properties.publicIPAddress.id",
            "primary": "properties.ipConfigurations.properties.primary",
        }
    ],
    "enable_accelerated_networking": "properties.enableAcceleratedNetworking",
    "dns_settings": {
        "dns_servers": "properties.dnsSettings.dnsServers",
        "internal_dns_name_label": "properties.dnsSettings.internalDnsNameLabel",
    },
    "network_security_group_id": "properties.networkSecurityGroup.id",
}


def convert_raw_to_present_state(hub, raw_state):
    return hub.tool.azure.generic.convert_state_format(
        raw_state,
        RAW_TO_PRESENT_MAP,
    )


def convert_present_to_raw_state(hub, present_state):
    return hub.tool.azure.generic.convert_state_format(
        present_state,
        PRESENT_TO_RAW_MAP,
    )
