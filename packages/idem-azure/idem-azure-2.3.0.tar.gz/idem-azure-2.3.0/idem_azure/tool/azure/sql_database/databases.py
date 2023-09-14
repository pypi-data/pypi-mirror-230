from collections import OrderedDict
from typing import Any
from typing import Dict


RAW_TO_PRESENT_PROPERTIES_NAMES_MAPPING = {
    "autoPauseDelay": "auto_pause_delay",
    "catalogCollation": "catalog_collation",
    "collation": "collation",
    "createMode": "create_mode",
    "elasticPoolId": "elastic_pool_id",
    "federatedClientId": "federated_client_id",
    "highAvailabilityReplicaCount": "high_availability_replica_count",
    "isLedgerOn": "is_ledger_on",
    "licenseType": "license_type",
    "longTermRetentionBackupResourceId": "long_term_retention_backup_resource_id",
    "maintenanceConfigurationId": "maintenance_configuration_id",
    "maxSizeBytes": "max_size_bytes",
    "minCapacity": "min_capacity",
    "readScale": "read_scale",
    "recoverableDatabaseId": "recoverable_database_id",
    "recoveryServicesRecoveryPointId": "recovery_services_recovery_point_id",
    "requestedBackupStorageRedundancy": "requested_backup_storage_redundancy",
    "restorableDroppedDatabaseId": "restorable_dropped_database_id",
    "restorePointInTime": "restore_point_in_time",
    "sampleName": "sample_name",
    "secondaryType": "secondary_type",
    "sourceDatabaseDeletionDate": "source_database_deletion_date",
    "sourceDatabaseId": "source_database_id",
    "sourceResourceId": "source_resource_id",
    "zoneRedundant": "zone_redundant",
}

PRESENT_TO_RAW_PROPERTIES_NAMES_MAPPING = {
    v: k for k, v in RAW_TO_PRESENT_PROPERTIES_NAMES_MAPPING.items()
}


def convert_raw_database_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
) -> Dict[str, Any]:
    """
    Converts raw databases api response into present function format

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_id = resource["id"]
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "servers": "server_name",
            "databases": "database_name",
        }
    )
    uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
        resource_id, uri_parameters
    )
    translated_resource = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "location": resource["location"],
        **uri_parameter_values,
    }
    if "identity" in resource:
        translated_resource[
            "identity"
        ] = hub.tool.azure.sql_database.databases.convert_raw_identity_to_present(
            resource["identity"]
        )
    if "sku" in resource:
        translated_resource[
            "sku"
        ] = hub.tool.azure.sql_database.databases.convert_raw_sku_to_present(
            resource["sku"]
        )
    if "tags" in resource:
        translated_resource["tags"] = resource["tags"]
    properties = resource.get("properties")
    for (
        parameter_raw,
        parameter_present,
    ) in RAW_TO_PRESENT_PROPERTIES_NAMES_MAPPING.items():
        if properties.get(parameter_raw):
            translated_resource[parameter_present] = properties.get(parameter_raw)
    return translated_resource


def convert_present_to_raw_database(
    hub,
    name: str,
    location: str,
    resource_id: str = None,
    subscription_id: str = None,
    identity: Dict = None,
    auto_pause_delay: int = None,
    catalog_collation: str = None,
    collation: str = None,
    create_mode: str = None,
    elastic_pool_id: str = None,
    federated_client_id: str = None,
    high_availability_replica_count: int = None,
    is_ledger_on: bool = None,
    license_type: str = None,
    long_term_retention_backup_resource_id: str = None,
    maintenance_configuration_id: str = None,
    max_size_bytes: int = None,
    min_capacity: float = None,
    read_scale: str = None,
    recoverable_database_id: str = None,
    recovery_services_recovery_point_id: str = None,
    requested_backup_storage_redundancy: str = None,
    restorable_dropped_database_id: str = None,
    restore_point_in_time: str = None,
    sample_name: str = None,
    secondary_type: str = None,
    source_database_deletion_date: str = None,
    source_database_id: str = None,
    source_resource_id: str = None,
    zone_redundant: bool = None,
    sku: Dict = None,
    tags: Dict = None,
) -> Dict[str, Any]:
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {"location": location, "properties": {}}
    if identity is not None:
        payload[
            "identity"
        ] = hub.tool.azure.sql_database.databases.convert_present_to_raw_identity(
            identity
        )
    if sku is not None:
        payload[
            "sku"
        ] = hub.tool.azure.sql_database.databases.convert_present_to_raw_sku(sku)
    if tags is not None:
        payload["tags"] = tags
    for (
        parameter_raw,
        parameter_present,
    ) in RAW_TO_PRESENT_PROPERTIES_NAMES_MAPPING.items():
        if locals()[parameter_present] is not None:
            payload["properties"][parameter_raw] = locals()[parameter_present]
    return payload


def update_database_payload(
    hub,
    existing_payload: Dict[str, Any],
    new_values: Dict[str, Any],
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
        A result dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages list.
    """
    result = {"result": True, "ret": None, "comment": []}
    is_updated = False
    new_payload = {"properties": {}}

    identity = (
        new_values.get("identity")
        if "identity" in new_values
        else existing_payload.get("identity")
    )
    if identity is not None:
        new_payload[
            "identity"
        ] = hub.tool.azure.sql_database.databases.convert_present_to_raw_identity(
            identity
        )
        is_updated = True

    sku = new_values.get("sku") if "sku" in new_values else existing_payload.get("sku")
    if sku is not None:
        new_payload[
            "sku"
        ] = hub.tool.azure.sql_database.databases.convert_present_to_raw_sku(sku)
        is_updated = True

    tags = (
        new_values.get("tags") if "tags" in new_values else existing_payload.get("tags")
    )
    if tags is not None:
        new_payload["tags"] = new_values["tags"]
        is_updated = True

    for (
        parameter_raw,
        parameter_present,
    ) in RAW_TO_PRESENT_PROPERTIES_NAMES_MAPPING.items():
        if (new_values.get(parameter_present) is not None) and (
            new_values[parameter_present] != existing_payload.get(parameter_present)
        ):
            new_payload["properties"][parameter_raw] = new_values.get(parameter_present)
            is_updated = True
        elif existing_payload.get(parameter_present) is not None:
            new_payload["properties"][parameter_raw] = existing_payload.get(
                parameter_present
            )

    for k, v in new_values.items():
        if v is None:
            continue
        if k in PRESENT_TO_RAW_PROPERTIES_NAMES_MAPPING:
            if (
                PRESENT_TO_RAW_PROPERTIES_NAMES_MAPPING[k]
                not in new_payload["properties"]
            ):
                new_payload["properties"][
                    PRESENT_TO_RAW_PROPERTIES_NAMES_MAPPING[k]
                ] = v
        else:
            new_payload[k] = v

    if is_updated:
        result["ret"] = new_payload
    return result


def convert_raw_sku_to_present(
    hub,
    sku: Dict[str, Any],
) -> Dict[str, Any]:
    # sku's fields are already lowercase single-word nouns, so no conversion is necessary
    return sku


def convert_raw_identity_to_present(
    hub,
    identity: Dict[str, Any],
) -> Dict[str, Any]:
    present_identity = {
        "type": identity.get("type"),
    }
    raw_ua_identities: Dict = identity.get("userAssignedIdentities")
    if raw_ua_identities is not None:
        present_ua_identities = {}
        for k, v in raw_ua_identities.items():
            present_ua_identities[k] = {
                "principal_id": v.get("principalId"),
                "client_id": v.get("clientId"),
            }
        present_identity["user_assigned_identities"] = present_ua_identities

    return present_identity


def convert_present_to_raw_sku(
    hub,
    sku: Dict[str, Any],
) -> Dict[str, Any]:
    # sku's fields are already lowercase single-word nouns, so no conversion is necessary
    return sku


def convert_present_to_raw_identity(
    hub,
    identity: Dict[str, Any],
) -> Dict[str, Any]:
    raw_identity = {
        "type": identity.get("type"),
    }

    present_ua_identities = identity.get("user_assigned_identities")
    if present_ua_identities is not None:
        raw_ua_identities = {}
        for k, v in present_ua_identities.items():
            raw_ua_identities[k] = {
                "principalId": v.get("principal_id"),
                "clientId": v.get("client_id"),
            }
        raw_identity["userAssignedIdentities"] = raw_ua_identities

    return raw_identity
