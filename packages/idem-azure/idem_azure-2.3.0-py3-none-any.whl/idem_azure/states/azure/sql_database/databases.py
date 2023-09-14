"""State module for managing SQL Databases."""

__contracts__ = ["resource"]

import copy
import uuid
from dataclasses import make_dataclass, field
from typing import Dict, Any


async def present(
    hub,
    ctx,
    name: str,
    location: str,
    resource_id: str = None,
    subscription_id: str = None,
    resource_group_name: str = None,
    server_name: str = None,
    database_name: str = None,
    identity: make_dataclass(
        "DatabaseIdentity",
        [
            ("tenant_id", str, field(default=None)),
            ("type", str, field(default=None)),
            (
                "user_assigned_identities",
                Dict[
                    str,
                    make_dataclass(
                        "DatabaseUserIdentity",
                        [
                            ("principal_id", str, field(default=None)),
                            ("client_id", str, field(default=None)),
                        ],
                    ),
                ],
                field(default=None),
            ),
        ],
    ) = None,
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
    sku: make_dataclass(
        "Sku",
        [
            ("capacity", int, field(default=None)),
            ("family", str, field(default=None)),
            ("name", str, field(default=None)),
            ("size", str, field(default=None)),
            ("tier", str, field(default=None)),
        ],
    ) = None,
    tags: Dict = None,
) -> Dict:
    r"""Create or update SQL Databases.

    Args:
        name(str):
            The identifier for this state.

        resource_id(str, Optional):
            SQL Database resource id on Azure

        resource_group_name(str, Optional):
            The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.

        server_name(str, Optional):
            The name of the server.

        database_name(str, Optional):
            The name of the database.

        subscription_id(str, Optional):
            The subscription ID that identifies an Azure subscription.

        location(str):
            Resource location.

        identity(Dict[str, Any], Optional):
            The Azure Active Directory identity of the database.

            * tenant_id(str, Optional):
                The Azure Active Directory tenant id.
            * type(str, Optional):
                The identity type
                    "None"
                    "UserAssigned"
            * user_assigned_identities(Dict[str, DatabaseUserIdentity], Optional):
                The resource ids of the user assigned identities to use. The values are Azure Active Directory identity configuration for a resource:
                    * client_id(str):
                        The Azure Active Directory client id.
                    * principal_id(str):
                        The Azure Active Directory principal id.

        auto_pause_delay(int, Optional):
            Time in minutes after which database is automatically paused. A value of -1 means that automatic pause is disabled

        catalog_collation(str, Optional):
            Collation of the metadata catalog.

        collation(str, Optional):
            The collation of the database.

        create_mode(str, Optional):
            Specifies the mode of database creation.
                "Default": regular database creation.
                "Copy": creates a database as a copy of an existing database. sourceDatabaseId must be specified as the resource ID of the source database.
                "Secondary": creates a database as a secondary replica of an existing database. sourceDatabaseId must be specified as the resource ID of the existing primary database.
                "PointInTimeRestore": Creates a database by restoring a point in time backup of an existing database. sourceDatabaseId must be specified as the resource ID of the existing database, and restorePointInTime must be specified.
                "Recovery": Creates a database by restoring a geo-replicated backup. sourceDatabaseId must be specified as the recoverable database resource ID to restore.
                "Restore": Creates a database by restoring a backup of a deleted database. sourceDatabaseId must be specified. If sourceDatabaseId is the database's original resource ID, then sourceDatabaseDeletionDate must be specified. Otherwise sourceDatabaseId must be the restorable dropped database resource ID and sourceDatabaseDeletionDate is ignored. restorePointInTime may also be specified to restore from an earlier point in time.
                "RestoreLongTermRetentionBackup": Creates a database by restoring from a long term retention vault. recoveryServicesRecoveryPointResourceId must be specified as the recovery point resource ID.

                Copy, Secondary, and RestoreLongTermRetentionBackup are not supported for DataWarehouse edition.

        elastic_pool_id(str, Optional):
            The resource identifier of the elastic pool containing this database.

        federated_client_id(str, Optional):
            The Client id used for cross tenant per database CMK scenario

        high_availability_replica_count(int, Optional):
            The number of secondary replicas associated with the database that are used to provide high availability. Not applicable to a Hyperscale database within an elastic pool.

        is_ledger_on(bool, Optional):
            Whether or not this database is a ledger database, which means all tables in the database are ledger tables. Note: the value of this property cannot be changed after the database has been created.

        license_type(str, Optional):
            The license type to apply for this database. LicenseIncluded if you need a license, or BasePrice if you have a license and are eligible for the Azure Hybrid Benefit.

        long_term_retention_backup_resource_id(str, Optional):
            The resource identifier of the long term retention backup associated with create operation of this database.

        maintenance_configuration_id(str, Optional):
            Maintenance configuration id assigned to the database. This configuration defines the period when the maintenance updates will occur.

        max_size_bytes(int, Optional):
            The max size of the database expressed in bytes.

        min_capacity(float, Optional):
            Minimal capacity that database will always have allocated, if not paused

        read_scale(str, Optional):
            The state of read-only routing. If enabled, connections that have application intent set to readonly in their connection string may be routed to a readonly secondary replica in the same region. Not applicable to a Hyperscale database within an elastic pool.

        recoverable_database_id(str, Optional):
            The resource identifier of the recoverable database associated with create operation of this database.

        recovery_services_recovery_point_id(str, Optional):
            The resource identifier of the recovery point associated with create operation of this database.

        requested_backup_storage_redundancy(str, Optional):
            The storage account type to be used to store backups for this database.

        restorable_dropped_database_id(str, Optional):
            The resource identifier of the restorable dropped database associated with create operation of this database.

        restore_point_in_time(str, Optional):
            Specifies the point in time (ISO8601 format) of the source database that will be restored to create the new database.

        sample_name(str, Optional):
            The name of the sample schema to apply when creating this database.

        secondary_type(str, Optional):
            The secondary type of the database if it is a secondary. Valid values are Geo and Named.

        source_database_deletion_date(str, Optional):
            Specifies the time that the database was deleted.

        source_database_id(str, Optional):
            The resource identifier of the source database associated with create operation of this database.

        source_resource_id(str, Optional):
            The resource identifier of the source associated with the create operation of this database.
            This property is only supported for DataWarehouse edition and allows to restore across subscriptions.
            When sourceResourceId is specified, sourceDatabaseId, recoverableDatabaseId, restorableDroppedDatabaseId and sourceDatabaseDeletionDate must not be specified and CreateMode must be PointInTimeRestore, Restore or Recover.
            When createMode is PointInTimeRestore, sourceResourceId must be the resource ID of the existing database or existing sql pool, and restorePointInTime must be specified.
            When createMode is Restore, sourceResourceId must be the resource ID of restorable dropped database or restorable dropped sql pool.
            When createMode is Recover, sourceResourceId must be the resource ID of recoverable database or recoverable sql pool.
            When source subscription belongs to a different tenant than target subscription, "x-ms-authorization-auxiliary" header must contain authentication token for the source tenant. For more details about "x-ms-authorization-auxiliary" header see https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/authenticate-multi-tenant

        zone_redundant(bool, Optional):
            Whether or not this database is zone redundant, which means the replicas of this database will be spread across multiple availability zones.

        sku(Dict[str, Any], Optional):
            The database SKU.

            * capacity(int, Optional):
                Capacity of the particular SKU.
            * family(str, Optional):
                If the service has different generations of hardware, for the same SKU, then that can be captured here.
            * name(str, Optional):
                The name of the SKU, typically, a letter + Number code, e.g. P3.
            * size(str, Optional):
                Size of the particular SKU
            * tier(str, Optional):
                The tier or edition of the particular SKU, e.g. Basic, Premium.

            The list of SKUs may vary by region and support offer. To determine the SKUs (including the SKU name, tier/edition, family, and capacity) that are available to your subscription in an Azure region, use the Capabilities_ListByLocation REST API or one of the following commands:
                Azure CLI
                az sql db list-editions -l <location> -o table

                PowerShell
                Get-AzSqlServerServiceObjective -Location <location>

        tags(Dict, Optional):
            Resource tags.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            my-sqldb:
              azure.sql_databases.database.present:
                - location: westeurope
                - subscription_id: 11111111-2222-3333-4444-555555555555
                - resource_group_name: default-rg
                - server_name: my-server-1
                - database_name: test-sqldb-1
                - sku:
                    name: Standard
                    tier: Standard
                    capacity: 10
                - collation: SQL_Latin1_General_CP1_CI_AS
                - max_size_bytes: 268435456000
                - read_scale: Disabled
                - requested_backup_storage_redundancy: Local
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
        # Create
        if ctx.get("test", False):
            # Return a proposed state by Idem state --test
            result["new_state"] = hub.tool.azure.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "location": location,
                    "resource_id": resource_id,
                    "subscription_id": subscription_id,
                    "resource_group_name": resource_group_name,
                    "server_name": server_name,
                    "database_name": database_name,
                    "identity": identity,
                    "auto_pause_delay": auto_pause_delay,
                    "catalog_collation": catalog_collation,
                    "collation": collation,
                    "create_mode": create_mode,
                    "elastic_pool_id": elastic_pool_id,
                    "federated_client_id": federated_client_id,
                    "high_availability_replica_count": high_availability_replica_count,
                    "is_ledger_on": is_ledger_on,
                    "license_type": license_type,
                    "long_term_retention_backup_resource_id": long_term_retention_backup_resource_id,
                    "maintenance_configuration_id": maintenance_configuration_id,
                    "max_size_bytes": max_size_bytes,
                    "min_capacity": min_capacity,
                    "read_scale": read_scale,
                    "recoverable_database_id": recoverable_database_id,
                    "recovery_services_recovery_point_id": recovery_services_recovery_point_id,
                    "requested_backup_storage_redundancy": requested_backup_storage_redundancy,
                    "restorable_dropped_database_id": restorable_dropped_database_id,
                    "restore_point_in_time": restore_point_in_time,
                    "sample_name": sample_name,
                    "secondary_type": secondary_type,
                    "source_database_deletion_date": source_database_deletion_date,
                    "source_database_id": source_database_id,
                    "source_resource_id": source_resource_id,
                    "zone_redundant": zone_redundant,
                    "sku": sku,
                    "tags": tags,
                },
            )
            result["comment"].append(
                f"Would create azure.sql_database.databases '{name}'"
            )
            return result
        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.sql_database.databases.convert_present_to_raw_database(
                subscription_id=subscription_id,
                name=name,
                location=location,
                identity=identity,
                auto_pause_delay=auto_pause_delay,
                catalog_collation=catalog_collation,
                collation=collation,
                create_mode=create_mode,
                elastic_pool_id=elastic_pool_id,
                federated_client_id=federated_client_id,
                high_availability_replica_count=high_availability_replica_count,
                is_ledger_on=is_ledger_on,
                license_type=license_type,
                long_term_retention_backup_resource_id=long_term_retention_backup_resource_id,
                maintenance_configuration_id=maintenance_configuration_id,
                max_size_bytes=max_size_bytes,
                min_capacity=min_capacity,
                read_scale=read_scale,
                recoverable_database_id=recoverable_database_id,
                recovery_services_recovery_point_id=recovery_services_recovery_point_id,
                requested_backup_storage_redundancy=requested_backup_storage_redundancy,
                restorable_dropped_database_id=restorable_dropped_database_id,
                restore_point_in_time=restore_point_in_time,
                sample_name=sample_name,
                secondary_type=secondary_type,
                source_database_deletion_date=source_database_deletion_date,
                source_database_id=source_database_id,
                source_resource_id=source_resource_id,
                zone_redundant=zone_redundant,
                sku=sku,
                tags=tags,
            )
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.computed.resource_url}",
                success_codes=[200, 201, 202],
                json=payload,
            )

            if response_put["status"] == 202:
                # Creating the database is in progress.
                # TODO: Use reconciler mechanism to wait for operation to complete
                result["rerun_data"] = {
                    "operation_id": str(uuid.uuid4()),
                    "operation_headers": dict(response_put.get("headers")),
                    "resource_id": f"{computed_resource_id}",
                    "resource_url": f"{computed_resource_url}",
                    "old_state": result["old_state"],
                }
                return result
            elif not response_put["result"] and response_put["status"] != 202:
                hub.log.debug(
                    f"Could not create azure.sql_database.databases {response_put['comment']} {response_put['ret']}"
                )
                result["comment"].extend(
                    hub.tool.azure.result_utils.extract_error_comments(response_put)
                )
                result["result"] = False
                return result
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.sql_database.databases.convert_raw_database_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                )

            result["comment"].append(f"Created azure.sql_database.databases '{name}'")
            return result

    else:
        # Update
        # Generate a new PUT operation payload with new values
        new_payload = hub.tool.azure.sql_database.databases.update_database_payload(
            existing_resource,
            {
                "id": resource_id,
                "location": location,
                "identity": identity,
                "auto_pause_delay": auto_pause_delay,
                "catalog_collation": catalog_collation,
                "collation": collation,
                "create_mode": create_mode,
                "elastic_pool_id": elastic_pool_id,
                "federated_client_id": federated_client_id,
                "high_availability_replica_count": high_availability_replica_count,
                "is_ledger_on": is_ledger_on,
                "license_type": license_type,
                "long_term_retention_backup_resource_id": long_term_retention_backup_resource_id,
                "maintenance_configuration_id": maintenance_configuration_id,
                "max_size_bytes": max_size_bytes,
                "min_capacity": min_capacity,
                "read_scale": read_scale,
                "recoverable_database_id": recoverable_database_id,
                "recovery_services_recovery_point_id": recovery_services_recovery_point_id,
                "requested_backup_storage_redundancy": requested_backup_storage_redundancy,
                "restorable_dropped_database_id": restorable_dropped_database_id,
                "restore_point_in_time": restore_point_in_time,
                "sample_name": sample_name,
                "secondary_type": secondary_type,
                "source_database_deletion_date": source_database_deletion_date,
                "source_database_id": source_database_id,
                "source_resource_id": source_resource_id,
                "zone_redundant": zone_redundant,
                "sku": sku,
                "tags": tags,
            },
        )
        if ctx.get("test", False):
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.sql_database.databases '{name}' has no property need to be updated."
                )
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.sql_database.databases.convert_raw_database_to_present(
                    resource=new_payload["ret"],
                    idem_resource_name=name,
                )
                result["comment"].append(
                    f"Would update azure.sql_database.databases '{name}'"
                )
            return result
        # PUT operation to update a resource
        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"azure.sql_database.databases '{name}' has no property need to be updated."
            )
            return result
        result["comment"].extend(new_payload["comment"])
        response_put = await hub.exec.request.json.put(
            ctx,
            url=f"{ctx.computed.resource_url}",
            success_codes=[200, 201, 202],
            json=new_payload["ret"],
        )

        if not response_put["result"]:
            hub.log.debug(
                f"Could not update azure.sql_database.databases {response_put['comment']} {response_put['ret']}"
            )
            result["result"] = False
            result["comment"].extend(
                hub.tool.azure.result_utils.extract_error_comments(response_put)
            )
            return result

        if response_put["status"] == 202:
            # Updating the database is in progress.
            # TODO: Use reconciler mechanism to wait for operation to complete
            result["rerun_data"] = {
                "operation_id": str(uuid.uuid4()),
                "operation_headers": dict(response_put.get("headers")),
                "resource_id": f"{computed_resource_id}",
                "resource_url": f"{computed_resource_url}",
                "old_state": result["old_state"],
            }
            return result
        elif not response_put["result"] and response_put["status"] != 202:
            hub.log.debug(
                f"Could not update azure.sql_database.databases {response_put['comment']} {response_put['ret']}"
            )
            result["comment"].extend(
                hub.tool.azure.result_utils.extract_error_comments(response_put)
            )
            result["result"] = False
            return result
        else:
            result[
                "new_state"
            ] = hub.tool.azure.sql_database.databases.convert_raw_database_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
            )

        result["comment"].append(f"Updated azure.sql_database.databases '{name}'")
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    server_name: str,
    database_name: str,
    subscription_id: str = None,
) -> Dict:
    r"""Delete SQL databases.

    Args:
        name(str):
            The identifier for this state.

        resource_group_name(str):
            The name of the resource group.

        server_name(str):
            The name of the server.

        database_name(str):
            The name of the database.

        subscription_id(str, Optional):
            Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.sql_database.databases.absent:
                - name: value
                - resource_group_name: value
                - server_name: value
                - database_name: value
    """

    # Resource deletion is handled via common recursive_contracts.init#call_absent() wrapper
    raise NotImplementedError


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all databases under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.sql_database.databases
    """
    result = {}
    ret_list = await hub.exec.azure.sql_database.databases.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe SQL database {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.sql_database.databases.present": [
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
