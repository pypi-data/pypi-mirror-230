"""State module for managing storage blob."""
import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    account_name: str,
    container_name: str,
    resource_group_name: str,
    subscription_id: str = None,
    resource_id: str = None,
    default_encryption_scope: str = None,
    deny_encryption_scope_override: bool = False,
    has_immutability_policy: bool = False,
    immutable_storage_with_versioning: bool = False,
    metadata: Dict = None,
    public_access: str = "Blob",
    remaining_retention_days: int = 0,
):
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id

    if resource_id is None:
        resource_id = (
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/"
            f"storageAccounts/{account_name}/blobServices/default/containers/{container_name}"
        )

    response_get = await hub.exec.azure.storage_resource_provider.storage_blob.get(
        ctx, resource_id=resource_id
    )

    if response_get["result"]:
        # 1. Resource is absent,
        if not response_get["ret"]:
            # Test mode
            if ctx.get("test", False):
                # Return a proposed state by Idem state --test
                result[
                    "new_state"
                ] = hub.tool.azure.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "resource_group_name": resource_group_name,
                        "account_name": account_name,
                        "container_name": container_name,
                        "subscription_id": subscription_id,
                        "resource_id": resource_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.storage_resource_provider.blob '{name}'"
                )
                return result
            # Create resource
            else:
                # PUT operation to create a resource
                payload = {
                    "id": resource_id,
                    "name": name,
                    "container_name": container_name,
                    "type": "Microsoft.Storage/storageAccounts/blobServices/containers",
                    "properties": {
                        "metadata": metadata,
                        "deleted": False,
                        "remainingRetentionDays": remaining_retention_days,
                        "publicAccess": public_access,
                        "hasImmutabilityPolicy": has_immutability_policy,
                        "hasLegalHold": False,
                    },
                }

                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                    success_codes=[200, 201],
                    json=payload,
                )

                if response_put["status"] == 404:
                    hub.log.debug(
                        f"Could not create azure.storage_resource_provider.storage_blob {response_put['comment']} {response_put['ret']}"
                    )
                    result["result"] = False
                    result["comment"].extend(
                        hub.tool.azure.result_utils.extract_error_comments(response_put)
                    )
                    return result
                elif response_put["status"] == 202:
                    get_response = {"result": False}
                    while not get_response["result"]:
                        get_response = await hub.exec.request.json.get(
                            ctx,
                            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                            success_codes=[200],
                        )
                    result[
                        "new_state"
                    ] = hub.tool.azure.storage_resource_provider.storage_blob.convert_raw_storage_blob_to_present(
                        subscription_id=subscription_id,
                        resource_grp_name=resource_group_name,
                        account_name=account_name,
                        result_dict=get_response["ret"],
                    )

                elif not response_put["result"] and response_put["status"] != 202:
                    hub.log.debug(
                        f"Could not create azure.storage_resource_provider.storage_blob {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"].extend(
                        hub.tool.azure.result_utils.extract_error_comments(response_put)
                    )
                    result["result"] = False
                    return result

                else:
                    result_payload = get_create_payload(
                        resource_id,
                        name,
                        container_name,
                        metadata,
                        resource_group_name,
                        remaining_retention_days,
                        public_access,
                        has_immutability_policy,
                    )
                    result[
                        "new_state"
                    ] = hub.tool.azure.storage_resource_provider.storage_blob.convert_raw_storage_blob_to_present(
                        subscription_id=subscription_id,
                        resource_grp_name=resource_group_name,
                        account_name=account_name,
                        result_dict=result_payload,
                    )

                result["comment"].append(
                    f"Created azure.storage_resource_provider.storage_blob '{name}'"
                )
                return result

        # 2. Resource is present,
        else:
            existing_resource = response_get["ret"]
            # Create old and new payloads
            result[
                "old_state"
            ] = hub.tool.azure.storage_resource_provider.storage_blob.convert_raw_storage_blob_to_present(
                subscription_id=subscription_id,
                resource_grp_name=resource_group_name,
                account_name=account_name,
                result_dict=existing_resource,
            )
            changed_resources = {
                "default_encryption_scope": default_encryption_scope,
                "deny_encryption_scope_override": deny_encryption_scope_override,
                "has_immutability_policy": has_immutability_policy,
                "immutable_storage_with_versioning": immutable_storage_with_versioning,
                "metadata": metadata,
                "remaining_retention_days": remaining_retention_days,
                "public_access": public_access,
            }
            # Generate PUT operation payload with new values
            new_payload = hub.tool.azure.storage_resource_provider.storage_blob.update_storage_blob_payload(
                existing_resource, changed_resources
            )

            # Test mode
            if ctx.get("test", False):
                # i. If no changed property found which needs to be updated.
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.storage_resource_provider.storage_blob '{name}' has no property need to be updated."
                    )
                # ii. Properties will be updated
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.storage_resource_provider.storage_blob.convert_raw_storage_blob_to_present(
                        subscription_id=subscription_id,
                        resource_grp_name=resource_group_name,
                        account_name=account_name,
                        result_dict=new_payload["ret"],
                    )
                    result["comment"].append(
                        f"Would update azure.storage_resource_provider.storage_blob '{name}'"
                    )
                return result

            # PUT operation nothing to update the resource
            if new_payload["ret"] == None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.storage_resource_provider.storage_blob '{name}' has no property need to be updated."
                )
                return result

            # Call PUT operation to update the resource
            result["comment"].extend(new_payload["comment"])
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                success_codes=[200],
                json=new_payload["ret"],
            )
            if response_put["result"] == False:
                hub.log.debug(
                    f"Could not update azure.storage_resource_provider.storage_blob {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"].extend(
                    hub.tool.azure.result_utils.extract_error_comments(response_put)
                )
                return result

            result[
                "new_state"
            ] = hub.tool.azure.storage_resource_provider.storage_blob.convert_raw_storage_blob_to_present(
                subscription_id=subscription_id,
                resource_grp_name=resource_group_name,
                account_name=account_name,
                result_dict=response_put["ret"],
            )
            if result["old_state"] == result["new_state"]:
                result["comment"].append(
                    f"azure.storage_resource_provider.storage_blob '{name}' has no property need to be updated."
                )
                return result

            result["comment"].append(
                f"Updated azure.storage_resource_provider.storage_blob '{name}'"
            )
            return result
    # 3. If issue occurred while finding resource
    else:
        hub.log.debug(
            f"Could not get azure.storage_resource_provider.storage_blob {response_get['comment']} {response_get['ret']}"
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
    account_name: str,
    container_name: str,
    subscription_id: str = None,
):
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    resource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/"
        f"storageAccounts/{account_name}/blobServices/default/containers/{container_name}"
    )
    response_get = await hub.exec.azure.storage_resource_provider.storage_blob.get(
        ctx,
        resource_id=resource_id,
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.storage_resource_provider.storage_blob '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"].extend(
            hub.tool.azure.result_utils.extract_error_comments(response_get)
        )
        return result

    if response_get["ret"]:
        result["old_state"] = response_get["ret"]
        result["old_state"]["name"] = name

        if ctx.get("test", False):
            result["comment"].append(
                f"Would delete azure.storage_resource_provider.storage_blob '{name}'"
            )
            return result
        response_delete = await hub.exec.request.raw.delete(
            ctx,
            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-06-01",
            success_codes=[200, 202],
        )

        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete azure.storage_resource_provider.storage_blob {response_delete['comment']} {response_delete['ret']}"
            )
            result["result"] = False
            result["comment"].extend(
                hub.tool.azure.result_utils.extract_error_comments(response_delete)
            )
            return result

        result["comment"].append(
            f"Deleted azure.storage_resource_provider.storage_blob '{name}'"
        )
        return result
    else:
        # If Azure returns 'Not Found' error, it means the resource has been absent.
        result["comment"].append(
            f"azure.storage_resource_provider.storage_blob '{name}' already absent"
        )
        return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    result = {}
    ret_list = await hub.exec.azure.storage_resource_provider.storage_blob.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe storage account {ret_list['comment']}")
        return result
    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.storage_resource_provider.storage_blob.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result


def get_create_payload(
    p_resource_id,
    p_name,
    p_container_name,
    p_metadata,
    resource_group_name,
    p_remaining_retention_days,
    p_public_access,
    p_has_immutability_policy,
):
    return {
        "id": p_resource_id,
        "name": p_name,
        "container_name": p_container_name,
        "resource_group_name": resource_group_name,
        "type": "Microsoft.Storage/storageAccounts/blobServices/containers",
        "properties": {
            "metadata": p_metadata,
            "deleted": False,
            "remainingRetentionDays": p_remaining_retention_days,
            "publicAccess": p_public_access,
            "hasImmutabilityPolicy": p_has_immutability_policy,
            "hasLegalHold": False,
        },
    }
