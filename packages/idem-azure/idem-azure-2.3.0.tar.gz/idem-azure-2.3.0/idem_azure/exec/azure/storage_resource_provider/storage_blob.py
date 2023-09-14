"""Exec module for managing storage account."""
from collections import OrderedDict
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def list_(hub, ctx) -> Dict:
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "resourceGroups": "resource_group_name",
            "storageAccounts": "account_name",
        }
    )

    # 1. List all available storage accounts
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Storage/storageAccounts?api-version=2021-04-01",
        success_codes=[200],
    ):
        resource_storage_accounts = page_result.get("value")
        if resource_storage_accounts:
            # 2. Iterate over storage accounts to get associated containers
            for resource_storage_account in resource_storage_accounts:
                resource_id = resource_storage_account["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )

                account_dict = hub.tool.azure.storage_resource_provider.storage_accounts.convert_raw_storage_accounts_to_present(
                    resource=resource_storage_account,
                    idem_resource_name=resource_id,
                    subscription_id=subscription_id,
                    resource_id=resource_id,
                    **uri_parameter_values,
                )

                if account_dict:
                    account_name = account_dict.get("account_name")
                    resource_grp_name = account_dict.get("resource_group_name")
                    async for page_result_internal in hub.tool.azure.request.paginate(
                        ctx,
                        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/resourceGroups/{resource_grp_name}"
                        f"/providers/Microsoft.Storage/storageAccounts/{account_name}/blobServices/default/containers?api-version=2022-09-01",
                        success_codes=[200],
                    ):
                        # 3. Get paginated list of storage_blobs
                        storage_blobs = page_result_internal.get("value")
                        if storage_blobs:
                            for blob_container in storage_blobs:
                                blob_dict = hub.tool.azure.storage_resource_provider.storage_blob.convert_raw_storage_blob_to_present(
                                    subscription_id,
                                    resource_grp_name,
                                    account_name,
                                    blob_container,
                                )
                                result["ret"].append(blob_dict)
    return result


async def get(hub, ctx, resource_id: str, name: str = None) -> Dict[str, Any]:
    result = dict(comment=[], result=True, ret=None)
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "storageAccounts": "account_name",
            "containerName": "container_name",
        }
    )

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
        success_codes=[200],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"].extend(
            hub.tool.azure.result_utils.extract_error_comments(response_get)
        )
        return result
    uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
        resource_id, uri_parameters
    )

    result[
        "ret"
    ] = hub.tool.azure.storage_resource_provider.storage_blob.convert_raw_storage_blob_to_present(
        uri_parameter_values.get("subscription_id"),
        uri_parameter_values.get("resource_group_name"),
        uri_parameter_values.get("account_name"),
        response_get["ret"],
    )

    return result
