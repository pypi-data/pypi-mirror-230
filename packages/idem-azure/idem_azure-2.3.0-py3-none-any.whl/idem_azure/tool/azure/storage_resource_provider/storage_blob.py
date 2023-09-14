from typing import Any
from typing import Dict


def fill_properties_original(translated_properties, source_properties):
    # default_encryption_scope
    if "defaultEncryptionScope" in source_properties:
        translated_properties["default_encryption_scope"] = source_properties[
            "defaultEncryptionScope"
        ]

    # deny_encryption_scope_override
    if "denyEncryptionScopeOverride" in source_properties:
        translated_properties["deny_encryption_scope_override"] = source_properties[
            "denyEncryptionScopeOverride"
        ]

    # has_immutability_policy
    if "hasImmutabilityPolicy" in source_properties:
        translated_properties["has_immutability_policy"] = source_properties[
            "hasImmutabilityPolicy"
        ]

    # immutable_storage_with_versioning, ??
    if "immutable_storage_with_versioning" in source_properties:
        translated_properties["immutable_storage_with_versioning"] = source_properties[
            "default_encryption_scope"
        ]

    # metadata,
    if "metadata" in source_properties:
        translated_properties["metadata"] = source_properties["metadata"]

    # public_access
    if "publicAccess" in source_properties:
        translated_properties["public_access"] = source_properties["publicAccess"]

    return translated_properties


def fill_properties_translated(translated_properties, source_properties):
    # default_encryption_scope
    if "default_encryption_scope" in source_properties:
        translated_properties["default_encryption_scope"] = source_properties[
            "default_encryption_scope"
        ]

    # deny_encryption_scope_override
    if "deny_encryption_scope_override" in source_properties:
        translated_properties["deny_encryption_scope_override"] = source_properties[
            "deny_encryption_scope_override"
        ]

    # has_immutability_policy
    if "has_immutability_policy" in source_properties:
        translated_properties["has_immutability_policy"] = source_properties[
            "has_immutability_policy"
        ]

    # immutable_storage_with_versioning, ??
    if "immutable_storage_with_versioning" in source_properties:
        translated_properties["immutable_storage_with_versioning"] = source_properties[
            "immutable_storage_with_versioning"
        ]

    # metadata,
    if "metadata" in source_properties:
        translated_properties["metadata"] = source_properties["metadata"]

    # public_access
    if "public_access" in source_properties:
        translated_properties["public_access"] = source_properties["public_access"]

    return translated_properties


def get_translated_resources(
    subscription_id,
    resource_grp_name,
    account_name,
    result_dict,
    original_or_translated,
):
    translated_resource = {
        "subscription_id": subscription_id,
        "resource_group_name": resource_grp_name,
        "account_name": account_name,
        "properties": {},
    }

    if result_dict.get("id"):
        translated_resource["resource_id"] = result_dict.get("id")

    elif result_dict.get("resource_id"):
        translated_resource["resource_id"] = result_dict.get("resource_id")

    if result_dict.get("name"):
        translated_resource["name"] = result_dict.get("name")

    if result_dict.get("type"):
        translated_resource["type"] = result_dict.get("type")

    if result_dict.get("etag"):
        translated_resource["etag"] = result_dict.get("etag")

    if result_dict.get("properties"):
        if original_or_translated:
            translated_resource["properties"] = fill_properties_original(
                translated_resource["properties"], result_dict.get("properties")
            )
        else:
            translated_resource["properties"] = fill_properties_translated(
                translated_resource["properties"], result_dict.get("properties")
            )
    else:
        translated_resource["properties"] = {}
    return translated_resource


def convert_raw_storage_blob_to_present(
    hub,
    subscription_id: str,
    resource_grp_name: str,
    account_name: str,
    result_dict: Dict = None,
) -> Dict[str, Any]:
    return get_translated_resources(
        subscription_id,
        resource_grp_name,
        account_name,
        result_dict,
        original_or_translated=True,
    )


def convert_present_to_raw_storage_blob(
    hub,
    subscription_id: str,
    resource_grp_name: str,
    account_name: str,
    name: str,
    has_immutability_policy: bool = False,
    immutable_storage_with_versioning: bool = False,
    metadata: Dict = None,
    public_access: str = None,
    remaining_retention_days: int = 0,
) -> Dict[str, Any]:
    result_dict = dict()
    if name:
        result_dict["name"] = name
    result_dict["immutable_storage_with_versioning"] = immutable_storage_with_versioning
    translated_resource = get_translated_resources(
        subscription_id,
        resource_grp_name,
        account_name,
        result_dict,
        original_or_translated=True,
    )
    translated_resource["properties"]["deleted"] = False
    translated_resource["properties"][
        "remainingRetentionDays"
    ] = remaining_retention_days
    translated_resource["properties"]["publicAccess"]: public_access
    translated_resource["properties"]["hasImmutabilityPolicy"] = has_immutability_policy
    if metadata:
        translated_resource["properties"]["metadata"] = metadata
    return translated_resource


def convert_raw_storage_blob_to_raw(
    hub,
    subscription_id: str,
    resource_grp_name: str,
    account_name: str,
    result_dict: Dict = None,
) -> Dict[str, Any]:
    return get_translated_resources(
        subscription_id,
        resource_grp_name,
        account_name,
        result_dict,
        original_or_translated=False,
    )


def update_storage_blob_payload(
    hub,
    existing_resources: Dict,
    changed_resources: Dict = None,
) -> Dict[str, Any]:
    result = {"result": True, "ret": None, "comment": []}
    resource_changed = False
    translated_resource = existing_resources

    # default_encryption_scope
    default_encryption_scope_changed = get_changed_resource(
        translated_resource["properties"].get("default_encryption_scope"),
        changed_resources["default_encryption_scope"],
    )
    if default_encryption_scope_changed:
        translated_resource["properties"][
            "default_encryption_scope"
        ] = changed_resources["default_encryption_scope"]
        resource_changed = True

    deny_encryption_scope_override_changed = get_changed_resource(
        translated_resource["properties"].get("deny_encryption_scope_override"),
        changed_resources["deny_encryption_scope_override"],
    )
    if deny_encryption_scope_override_changed:
        translated_resource["properties"][
            "deny_encryption_scope_override"
        ] = changed_resources["deny_encryption_scope_override"]
        resource_changed = True

    has_immutability_policy_changed = get_changed_resource(
        translated_resource["properties"].get("has_immutability_policy"),
        changed_resources["has_immutability_policy"],
    )
    if has_immutability_policy_changed:
        translated_resource["properties"][
            "has_immutability_policy"
        ] = changed_resources["has_immutability_policy"]
        resource_changed = True

    immutable_storage_with_versioning_changed = get_changed_resource(
        translated_resource["properties"].get("has_immutability_policy"),
        changed_resources["has_immutability_policy"],
    )
    if immutable_storage_with_versioning_changed:
        translated_resource["properties"][
            "has_immutability_policy"
        ] = changed_resources["has_immutability_policy"]
        resource_changed = True

    if translated_resource["properties"].get("metadata"):
        metadata_changed = get_changed_resource(
            translated_resource["properties"].get("metadata"),
            changed_resources["metadata"],
        )
        if metadata_changed:
            translated_resource["properties"]["metadata"] = changed_resources[
                "metadata"
            ]
            resource_changed = True
    else:
        translated_resource["properties"]["metadata"] = changed_resources["metadata"]
        resource_changed = True

    public_access_changed = get_changed_resource(
        translated_resource["properties"].get("public_access"),
        changed_resources["public_access"],
    )
    if public_access_changed:
        translated_resource["properties"]["public_access"] = changed_resources[
            "public_access"
        ]
        resource_changed = True

    if resource_changed:
        result["ret"] = translated_resource
    else:
        result["ret"] = None
    return result


def get_changed_resource(original_res, changed_res):
    res = None
    if original_res:
        if changed_res:
            if original_res != changed_res:
                res = changed_res
        else:
            res = changed_res
    else:
        res = changed_res
    return res
