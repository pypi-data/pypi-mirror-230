RAW_TO_PRESENT_MAP = {
    "subscription_id": "subscriptionId",
    "resource_group_name": "resourceGroupName",
    "virtual_network_name": "virtualNetworkName",
    "virtual_network_peering_name": "virtualNetworkPeeringName",
    "allow_virtual_network_access": "properties.allowVirtualNetworkAccess",
    "allow_forwarded_traffic": "properties.allowForwardedTraffic",
    "allow_gateway_transit": "properties.allowGatewayTransit",
    "use_remote_gateways": "properties.useRemoteGateways",
    "remote_virtual_network": {"id": "properties.remoteVirtualNetwork.id"},
    "do_not_verify_remote_gateways": "properties.doNotVerifyRemoteGateways",
}


PRESENT_TO_RAW_MAP = {
    "subscriptionId": "subscription_id",
    "resourceGroupName": "resource_group_name",
    "virtualNetworkName": "virtual_network_name",
    "virtualNetworkPeeringName": "virtual_network_peering_name",
    "properties": {
        "allowVirtualNetworkAccess": "allow_virtual_network_access",
        "allowForwardedTraffic": "allow_forwarded_traffic",
        "allowGatewayTransit": "allow_gateway_transit",
        "useRemoteGateways": "use_remote_gateways",
        "remoteVirtualNetwork": {"id": "remote_virtual_network.id"},
        "doNotVerifyRemoteGateways": "do_not_verify_remote_gateways",
    },
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
