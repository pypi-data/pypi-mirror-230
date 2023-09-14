import copy
from typing import Any
from typing import Dict
from typing import List


def convert_key_vault_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    resource_id: str,
    vault_name: str,
    subscription_id: str = None,
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate a Dict that match the format of
    present input parameters.

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        resource_group_name: Azure Resource Group name.
        vault_name: Azure vault resource name.
        resource_id: Azure vault resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
      A Dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "subscription_id": subscription_id,
        "vault_name": vault_name,
        "location": resource["location"],
    }
    if "tags" in resource:
        resource_translated["tags"] = resource["tags"]
    if "properties" in resource:
        resource_translated["properties"] = resource["properties"]
    if "type" in resource:
        resource_translated["type"] = resource["type"]
    if "systemData" in resource:
        resource_translated["system_data"] = resource["systemData"]
    return resource_translated


def convert_present_to_key_vault(
    hub,
    location: str,
    sku: Dict[str, Any] = None,
    tags: Dict = None,
    tenant_id: str = None,
    enabled_for_deployment: bool = None,
    enabled_for_disk_encryption: bool = None,
    enabled_for_template_deployment: bool = None,
    enable_rbac_authorization: bool = None,
    public_network_access_enabled: str = None,
    soft_delete_retention_days: int = None,
    purge_protection_enabled: bool = None,
    access_policies: List[Dict[str, Any]] = None,
    network_acls: Dict[str, Any] = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        location(str): Resource location. Changing this forces a new resource to be created.
        sku(Dict, Optional): The SKU of the key vault.
        tags(Dict, Optional): Resource tags.
        tenant_id(str, Optional): Tenant id of azure account.
        enabled_for_deployment(bool, Optional): Boolean flag to specify whether Azure Virtual Machines are permitted to retrieve certificates stored as secrets from the key vault.
        enabled_for_disk_encryption(bool, Optional): Boolean flag to specify whether Azure Disk Encryption is permitted to retrieve secrets from the vault and unwrap keys.
        enabled_for_template_deployment(bool, Optional):  Boolean flag to specify whether Azure Resource Manager is permitted to retrieve secrets from the key vault.
        enable_rbac_authorization(bool, Optional): Boolean flag to specify whether Azure Key Vault uses Role Based Access Control (RBAC) for authorization of data actions.
        public_network_access_enabled(str, Optional): Whether public network access is allowed for this Key Vault. Defaults to true
        soft_delete_retention_days(int, Optional): The number of days that items should be retained for once soft-deleted. This value can be between 7 and 90 (the default) days.
        purge_protection_enabled(bool, Optional): Is Purge Protection enabled for this Key Vault?
        access_policies(List[Dict[str, Any]], Optional): Key vault access policies.
        network_acls(Dict[str, Any], Optional): Key vault Network Acl.
    Returns:
        A Dict in the format of an Azure PUT operation payload.
    """
    payload = {"location": location, "properties": {}}
    if tags is not None:
        payload["tags"] = tags
    payload["properties"]["sku"] = {
        "name": sku.get("name") if sku else "Standard",
        "family": sku.get("family") if sku else "A",
    }
    payload["properties"]["tenantId"] = tenant_id
    if enabled_for_deployment is not None:
        payload["properties"]["enabledForDeployment"] = enabled_for_deployment
    if enabled_for_disk_encryption is not None:
        payload["properties"]["enabledForDiskEncryption"] = enabled_for_disk_encryption
    if enabled_for_template_deployment is not None:
        payload["properties"][
            "enabledForTemplateDeployment"
        ] = enabled_for_template_deployment
    if public_network_access_enabled is not None:
        payload["properties"]["publicNetworkAccess"] = public_network_access_enabled
    if enable_rbac_authorization is not None:
        payload["properties"]["enableRbacAuthorization"] = enable_rbac_authorization
    if soft_delete_retention_days is not None:
        payload["properties"]["softDeleteRetentionInDays"] = soft_delete_retention_days
    if purge_protection_enabled is not None:
        payload["properties"]["enablePurgeProtection"] = purge_protection_enabled
    payload["properties"]["accessPolicies"] = (
        convert_present_to_access_policies(access_policies) if access_policies else []
    )
    if network_acls is not None:
        payload["properties"]["networkAcls"] = convert_present_to_network_acl(
            network_acls
        )
    return payload


def convert_present_to_access_policies(access_policies: List[Dict[str, Any]]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        access_policies(List[Dict[str, Any]]) : List of access policies for key vault.

    Returns:
        List of access policies for key vault payload List[Dict[str, Any]] in the format of an Azure PUT operation payload.
    """
    access_policies_list: List = []
    for access_policy in access_policies:
        access_policies_payload = {
            "tenantId": access_policy.get("tenant_id"),
            "objectId": access_policy.get("object_id"),
        }
        access_policies_payload["permissions"] = {}
        if access_policy.get("key_permissions") is not None:
            access_policies_payload["permissions"]["keys"] = access_policy.get(
                "key_permissions"
            )
        if access_policy.get("secret_permissions") is not None:
            access_policies_payload["permissions"]["secrets"] = access_policy.get(
                "secret_permissions"
            )
        if access_policy.get("certificate_permissions") is not None:
            access_policies_payload["permissions"]["certificates"] = access_policy.get(
                "certificate_permissions"
            )
        if access_policy.get("storage_permissions") is not None:
            access_policies_payload["permissions"]["storage"] = access_policy.get(
                "storage_permissions"
            )
        access_policies_list.append(access_policies_payload)
    return access_policies_list


def convert_present_to_network_acl(network_acls: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        network_acls(Dict(str, Any)) : Specifies information about the Network Acl for key vault.

    Returns:
        Network Acl Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    network_acls_payload = {
        "bypass": network_acls.get("bypass"),
        "defaultAction": network_acls.get("default_action"),
        "ipRules": network_acls.get("ip_rules"),
        "virtualNetworkRules": network_acls.get("virtual_network_subnet_ids"),
    }
    return network_acls_payload


def update_key_vault_payload(
    hub, existing_payload: Dict[str, Any], new_values: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate an updated payload, which can be used by
    PUT operation to update a resource on Azure.

    Args:
        hub: The redistributed pop central hub.
        existing_payload: An existing resource state from Azure. This is usually a GET operation response.
        new_values: A dictionary of desired state values. If any property's value is None,
        this property will be ignored. This is to match the behavior when a present() input is a None, Idem does not
        do an update.

    Returns:
        A result Dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages list.
    """
    result = {"result": True, "ret": None, "comment": []}
    need_update = False
    new_payload = copy.deepcopy(existing_payload)
    if (new_values.get("tags") is not None) and (
        existing_payload.get("tags") != new_values.get("tags")
    ):
        new_payload["tags"] = new_values["tags"]
        need_update = True
    if need_update:
        result["ret"] = new_payload
    return result
