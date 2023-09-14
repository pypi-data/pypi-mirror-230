"""States module for managing Key Vault."""
import copy
from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]
__reconcile_wait__ = {"static": {"wait_in_seconds": 20}}


async def present(
    hub,
    ctx,
    name: str,
    location: str,
    resource_group_name: str,
    vault_name: str,
    sku: make_dataclass(
        "sku",
        [("name", str, field(default=None)), ("family", str, field(default=None))],
    ) = None,
    tenant_id: str = None,
    soft_delete_retention_days: int = None,
    subscription_id: str = None,
    resource_id: str = None,
    tags: Dict = None,
    enabled_for_deployment: bool = None,
    enabled_for_disk_encryption: bool = None,
    enabled_for_template_deployment: bool = None,
    enable_rbac_authorization: bool = None,
    public_network_access_enabled: str = None,
    purge_protection_enabled: bool = None,
    access_policies: List[
        make_dataclass(
            "accessPolicies",
            [
                ("tenant_id", str, field(default=None)),
                ("object_id", str, field(default=None)),
                ("key_permissions", List[str], field(default=None)),
                ("secret_permissions", List[str], field(default=None)),
                ("storage_permissions", List[str], field(default=None)),
                ("certificate_permissions", List[str], field(default=None)),
            ],
        )
    ] = None,
    network_acls: make_dataclass(
        "networkAcls",
        [
            ("bypass", str, field(default=None)),
            ("default_action", str, field(default=None)),
            ("ip_rules", List[str], field(default=None)),
            ("virtual_network_subnet_ids", List[str], field(default=None)),
        ],
    ) = None,
) -> Dict:
    r"""Create or update key vault.

    Args:

        name(str): The identifier for this state.
        location(str): Resource location. Changing this forces a new resource to be created.
        resource_group_name(str): The name of the resource group.
        vault_name(str): The name of the key vault.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Key vault resource id on Azure
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
        Dict

    Examples:
        .. code-block:: sls

            resource_is_present:
               test-azure-key-vault:
                  azure.key_vault.vault.present:
                      - name: test-key-vault
                      - vault_name: test-key-vault
                      - resource_group_name: azure-resource-group
                      - location: eastus
                      - sku:
                          family: A
                          name: Premium
                      - soft_delete_retention_days: 8
                      - tags:
                          test: test-Ashu
                      - enabled_for_deployment: false
                      - enabled_for_disk_encryption: true
                      - enabled_for_template_deployment: true
                      - enable_rbac_authorization: true
                      - public_network_access_enabled: Enabled
                      - purge_protection_enabled: true
                      - access_policies:
                          - object_id: 00000000-0000-0000-0000-000000000000
                            certificate_permissions:
                              - Get
                              - List
                              - Update
                              - Create
                              - Import
                              - Delete
                              - Recover
                              - Backup
                              - Restore
                              - ManageContacts
                              - ManageIssuers
                              - GetIssuers
                              - ListIssuers
                              - SetIssuers
                              - DeleteIssuers
                            key_permissions:
                              - Get
                              - List
                              - Update
                              - Create
                              - Import
                              - Delete
                              - Recover
                              - Backup
                              - Restore
                              - GetRotationPolicy
                              - SetRotationPolicy
                              - Rotate
                            secret_permissions:
                              - Get
                              - List
                              - Set
                              - Delete
                              - Recover
                              - Backup
                              - Restore
                            tenant_id: 00000000-0000-0000-0000-000000000000
                      - network_acls:
                          bypass: AzureServices
                          default_action: Deny
                          ip_rules: []
                          virtual_network_subnet_ids: []

    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }
    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    if tenant_id is None:
        tenant_id = ctx.acct.tenant
    if resource_id is None:
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.KeyVault/vaults/{vault_name}"
    response_get = await hub.exec.azure.key_vault.vault.get(
        ctx, resource_id=resource_id, raw=True
    )
    if response_get["result"]:
        if response_get["ret"] is None:
            if ctx.get("test", False):
                # Return a proposed state by Idem state --test
                result[
                    "new_state"
                ] = hub.tool.azure.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "resource_group_name": resource_group_name,
                        "subscription_id": subscription_id,
                        "location": location,
                        "resource_id": resource_id,
                        "vault_name": vault_name,
                        "sku": sku,
                        "soft_delete_retention_days": soft_delete_retention_days,
                        "purge_protection_enabled": purge_protection_enabled,
                        "tenant_id": tenant_id,
                        "access_policies": access_policies,
                        "network_acls": network_acls,
                        "enabled_for_deployment": enabled_for_deployment,
                        "enabled_for_disk_encryption": enabled_for_disk_encryption,
                        "enabled_for_template_deployment": enabled_for_template_deployment,
                        "enable_rbac_authorization": enable_rbac_authorization,
                        "public_network_access_enabled": public_network_access_enabled,
                        "tags": tags,
                    },
                )
                result["comment"].append(f"Would create azure.key_vault.vault '{name}'")
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.key_vault.vault.convert_present_to_key_vault(
                    location=location,
                    tags=tags,
                    sku=sku,
                    tenant_id=tenant_id,
                    enabled_for_deployment=enabled_for_deployment,
                    enabled_for_disk_encryption=enabled_for_disk_encryption,
                    enabled_for_template_deployment=enabled_for_template_deployment,
                    enable_rbac_authorization=enable_rbac_authorization,
                    public_network_access_enabled=public_network_access_enabled,
                    soft_delete_retention_days=soft_delete_retention_days,
                    purge_protection_enabled=purge_protection_enabled,
                    access_policies=access_policies,
                    network_acls=network_acls,
                )

                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                    success_codes=[200, 201],
                    json=payload,
                )
                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create key vault {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"].extend(
                        hub.tool.azure.result_utils.extract_error_comments(response_put)
                    )
                    result["result"] = False
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.key_vault.vault.convert_key_vault_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    vault_name=vault_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(f"Created azure.key_vault.vault '{name}'")
                return result

        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.key_vault.vault.convert_key_vault_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                vault_name=vault_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.key_vault.vault.update_key_vault_payload(
                existing_resource, {"tags": tags}
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.key_vault.vault '{name}' doesn't need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.key_vault.vault.convert_key_vault_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        vault_name=vault_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )
                    result["comment"].append(
                        f"Would update azure.key_vault.vault '{name}'"
                    )
                return result

            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.key_vault.vault '{name}' doesn't need to be updated."
                )
                return result
            result["comment"].extend(new_payload["comment"])
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                success_codes=[200, 201],
                json=new_payload["ret"],
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.key_vault.vault {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"].extend(
                    hub.tool.azure.result_utils.extract_error_comments(response_put)
                )
                return result

            result[
                "new_state"
            ] = hub.tool.azure.key_vault.vault.convert_key_vault_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                vault_name=vault_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(f"Updated azure.key_vault.vault '{name}'")
            return result
    else:
        hub.log.debug(
            f"Could not get azure.key_vault.vault {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"].extend(
            hub.tool.azure.result_utils.extract_error_comments(response_get)
        )
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    vault_name: str,
    subscription_id: str = None,
) -> dict:
    r"""Delete a key vault.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        vault_name(str): The name of the key vault.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.key_vault.vault.absent:
                - name: my-kv
                - subscription_id: my-subscription
                - resource_group_name: my-resource-group
                - vault_name: my-fp
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }
    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.KeyVault/vaults/{vault_name}"
    response_get = await hub.exec.azure.key_vault.vault.get(
        ctx, resource_id=resource_id, raw=True
    )
    if response_get["result"]:
        if response_get["ret"]:
            result[
                "old_state"
            ] = hub.tool.azure.key_vault.vault.convert_key_vault_to_present(
                resource=response_get["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                vault_name=vault_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.key_vault.vault '{vault_name}'"
                )
                return result
            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                success_codes=[200, 202],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.key_vault.vault {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"].extend(
                    hub.tool.azure.result_utils.extract_error_comments(response_delete)
                )
                return result
            result["comment"].append(f"Deleted azure.key_vault.vault '{vault_name}'")
            return result
        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.key_vault.vault '{vault_name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not azure.key_vault.vault '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"].extend(
            hub.tool.azure.result_utils.extract_error_comments(response_get)
        )
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all key vault under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.key_vault.vault
    """
    result = {}
    ret_list = await hub.exec.azure.key_vault.vault.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe key_vault vault {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.key_vault.vault.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result
