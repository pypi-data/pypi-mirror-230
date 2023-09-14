"""State module for managing Disks."""
from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    location: str,
    disk_name: str = None,
    resource_group_name: str = None,
    creation_data: make_dataclass(
        "CreationData",
        [
            ("create_option", str, field(default=None)),
            (
                "gallery_image_reference",
                make_dataclass(
                    "ImageDiskReference",
                    [
                        ("id", str, field(default=None)),
                        ("lun", int, field(default=None)),
                    ],
                ),
                field(default=None),
            ),
            (
                "image_reference",
                make_dataclass(
                    "ImageReference",
                    [
                        ("id", str, field(default=None)),
                        ("lun", int, field(default=None)),
                    ],
                ),
                field(default=None),
            ),
            ("logical_sector_size", int, field(default=None)),
            ("security_data_uri", str, field(default=None)),
            ("source_resource_id", str, field(default=None)),
            ("source_unique_id", str, field(default=None)),
            ("source_uri", str, field(default=None)),
            ("storage_account_id", str, field(default=None)),
            ("upload_size_bytes", int, field(default=None)),
        ],
    ) = None,
    extended_location: make_dataclass(
        "ExtendedLocation",
        [("name", str, field(default=None)), ("type", str, field(default=None))],
    ) = None,
    bursting_enabled: bool = None,
    data_access_auth_mode: make_dataclass(
        "DataAccessAuthMode",
        [
            ("azure_active_directory", str, field(default=None)),
        ],
    ) = None,
    disk_access_id: str = None,
    disk_iops_read_only: int = None,
    disk_iops_read_write: int = None,
    disk_mbps_read_only: int = None,
    disk_mbps_read_write: int = None,
    disk_size_gb: int = None,
    encryption: make_dataclass(
        "Encryption",
        [
            ("disk_encryption_set_id", str, field(default=None)),
            ("type", str, field(default=None)),
        ],
    ) = None,
    encryption_settings_collection: make_dataclass(
        "EncryptionSettingsCollection",
        [
            ("enabled", bool, field(default=None)),
            (
                "encryption_settings",
                make_dataclass(
                    "EncryptionSettings",
                    [
                        (
                            "disk_encryption_key",
                            make_dataclass(
                                "DiskEncryptionKey",
                                [
                                    ("secret_url", str, field(default=None)),
                                    (
                                        "source_vault",
                                        make_dataclass(
                                            "SourceVault",
                                            [("vm_uri", str, field(default=None))],
                                        ),
                                        field(default=None),
                                    ),
                                ],
                            ),
                            field(default=None),
                        ),
                        (
                            "key_encryption_key",
                            make_dataclass(
                                "KeyEncryptionKey",
                                [
                                    ("key_url", str, field(default=None)),
                                    (
                                        "source_vault",
                                        make_dataclass(
                                            "SourceVault",
                                            [("vm_uri", str, field(default=None))],
                                        ),
                                        field(default=None),
                                    ),
                                ],
                            ),
                            field(default=None),
                        ),
                    ],
                ),
                field(default=None),
            ),
            ("encryption_settings_version", str, field(default=None)),
        ],
    ) = None,
    hyper_v_generation: str = None,
    max_shares: int = None,
    network_access_policy: str = None,
    os_type: str = None,
    public_network_access: str = None,
    security_profile: make_dataclass(
        "SecurityProfile",
        [
            ("secure_vm_disk_encryption_set_id", str, field(default=None)),
            ("security_type", str, field(default=None)),
        ],
    ) = None,
    tier: str = None,
    sku: make_dataclass(
        "DiskSku",
        [("name", str, field(default=None)), ("tier", str, field(default=None))],
    ) = None,
    tags: Dict[str, str] = None,
    zones: List[str] = None,
    resource_id: str = None,
    subscription_id: str = None,
) -> Dict:
    r"""Create or update Disks.

    Args:
        name(str): The identifier for this state.
        disk_name(str, Optional): The name of the managed disk that is being created.
        resource_group_name(str, Optional): The name of the resource group.
        creation_data(Dict[str, Any], Optional):
            Disk source information. CreationData information cannot be changed after the disk has been created.

            * create_option (str, Optional):
                Enumerates the possible sources of a disk's creation.
                    Enum type. Allowed values:
                        - "Attach" - Disk will be attached to a VM.
                        - "Copy" - Create a new disk or snapshot by copying from a disk or snapshot specified by the given sourceResourceId.
                        - "CopyStart" - Create a new disk by using a deep copy process, where the resource creation is considered complete only after all data has been copied from the source.
                        - "Empty" - Create an empty data disk of a size given by disk_size_gb.
                        - "FromImage" - Create a new disk from a platform image specified by the given imageReference or galleryImageReference.
                        - "Import" - Create a disk by importing from a blob specified by a sourceUri in a storage account specified by storageAccountId.
                        - "ImportSecure" - Similar to Import create option. Create a new Trusted Launch VM or Confidential VM supported disk by importing additional blob for VM guest state specified by securityDataUri in storage account specified by storageAccountId.
                        - "Restore" - Create a new disk by copying from a backup recovery point.
                        - "Upload" - Create a new disk by obtaining a write token and using it to directly upload the contents of the disk.
                        - "UploadPreparedSecure" - Similar to Upload create option. Create a new Trusted Launch VM or Confidential VM supported disk and upload using write token in both disk and VM guest state

            * gallery_image_reference(List(Dict[str, Any])):
                Required if creating from a Gallery Image. The id of the ImageDiskReference will be the ARM id of the shared galley image version from which to create a disk.
                    * id(str, Optional):
                        A relative uri containing either a Platform Image Repository or user image reference.
                    * lun(str, Optional):
                        If the disk is created from an image's data disk, this is an index that indicates which of the data disks in the image to use. For OS disks, this field is null.
            * image_reference(List(Dict[str, Any])):
                Disk source information.
                    * id(str, Optional):
                        A relative uri containing either a Platform Image Repository or user image reference.
                    * lun(str, Optional):
                        If the disk is created from an image's data disk, this is an index that indicates which of the data disks in the image to use. For OS disks, this field is null.
            * logical_sector_size(str, Optional):
                Logical sector size in bytes for Ultra disks. Supported values are 512 ad 4096. 4096 is the default.
            * security_data_url(str, Optional):
                If createOption is ImportSecure, this is the URI of a blob to be imported into VM guest state.
            * source_resource_id(str, Optional):
                If createOption is Copy, this is the ARM id of the source snapshot or disk.
            * source_unique_id(str, Optional):
                If this field is set, this is the unique id identifying the source of this resource.
            * source_uri(str, Optional):
                If createOption is Import, this is the URI of a blob to be imported into a managed disk.
            * storage_account_id(str, Optional):
                Required if createOption is Import. The Azure Resource Manager identifier of the storage account containing the blob to import as a disk.
            * upload_size_bytes(str, Optional):
                If createOption is Upload, this is the size of the contents of the upload including the VHD footer. This value should be between 20972032 (20 MiB + 512 bytes for the VHD footer) and 35183298347520 bytes (32 TiB + 512 bytes for the VHD footer).
        location(str, Optional): Resource location.
        os_type(str, Optional): the Operating System type.
        disk_size_gb(int, Optional): If creationData.createOption is Empty, this field is mandatory, and it indicates the size of the disk to create. If this field is present for updates or creation with other options, it indicates a resize. Resizes are only allowed if the disk is not attached to a running VM, and can only increase the disk's size.
        encryption_settings_collection(Dict[str, Any], Optional): encryptionSettingsCollection

            * enabled(bool, Optional): Set this flag to true and provide DiskEncryptionKey and optional KeyEncryptionKey to enable encryption. Set this flag to false and remove DiskEncryptionKey and KeyEncryptionKey to disable encryption. If EncryptionSettings is null in the request object, the existing settings remain unchanged.
            * encryption_settings(List[Dict[str, Any]], Optional): A collection of encryption settings, one for each disk volume.
                * disk_encryption_key(Dict[str, Any], Optional): diskEncryptionKey
                    * source_vault(Dict[str, Any], Optional): sourceVault
                        * id(str, Optional): Resource Id
                    * secret_url(str, Optional): Url pointing to a key or secret in KeyVault
                * key_encryption_key(Dict[str, Any], Optional): keyEncryptionKey
                    * source_vault(Dict[str, Any], Optional): sourceVault
                        * id(str, Optional): Resource Id
                    * key_url(str, Optional): Url pointing to a key or secret in KeyVault
            * encryption_settings_version(str, Optional): Describes what type of encryption is used for the disks. Once this field is set, it cannot be overwritten. '1.0' corresponds to Azure Disk Encryption with AAD app.'1.1' corresponds to Azure Disk Encryption.
        disk_iops_read_write(int, Optional): The number of IOPS allowed for this disk; only settable for UltraSSD disks. One operation can transfer between 4k and 256k bytes.
        disk_mbps_read_write(int, Optional): The bandwidth allowed for this disk; only settable for UltraSSD disks. MBps means millions of bytes per second - MB here uses the ISO notation, of powers of 10.
        disk_iops_read_only(int, Optional): The total number of IOPS that will be allowed across all VMs mounting the shared disk as ReadOnly. One operation can transfer between 4k and 256k bytes.
        disk_mbps_read_only(int, Optional): The total throughput (MBps) that will be allowed across all VMs mounting the shared disk as ReadOnly. MBps means millions of bytes per second - MB here uses the ISO notation, of powers of 10.
        hyper_v_generation(str, Optional): The hypervisor generation of the Virtual Machine. Applicable to OS disks only.
        max_shares(int, Optional): The maximum number of VMs that can attach to the disk at the same time. Value greater than one indicates a disk that can be mounted on multiple VMs at the same time.
        encryption(Dict[str, Any], Optional): encryption
            * disk_encryption_set_id(str, Optional): ResourceId of the disk encryption set to use for enabling encryption at rest.
            * type(str, Optional): The type of key used to encrypt the data of the disk.
        network_access_policy (str, Optional): Policy for accessing the disk via network.
        disk_access_id (str, Optional): ARM id of the DiskAccess resource for using private endpoints on disks.
        tier (str, Optional): Performance tier of the disk (e.g, P4, S10) as described here: https://azure.microsoft.com/en-us/pricing/details/managed-disks/. Does not apply to Ultra disks.
        extended_location(dict[str, Any], Optional): The extended location where the disk will be created. Extended location cannot be changed.
        bursting_enabled(bool, Optional): Set to true to enable bursting beyond the provisioned performance target of the disk. Bursting is disabled by default. Does not apply to Ultra disks.
        security_profile(): Contains the security related information for the resource.
        public_network_access(str, Optional): Policy for controlling export on the disk.
        data_access_auth_mode(str, Optional): Additional authentication requirements when exporting or uploading to a disk or snapshot.
        tags(Dict[str, str], Optional): Resource tags. Defaults to None.
        sku(Dict[str, Any], Optional): The disks sku name. Defaults to None.
            * name(str, Optional): The sku name.
            * tier(str, Optional): The sku tier.
        zones(List(str), Optional): The Logical zone list for Disk.
        resource_id(str, Optional): Disk resource id on Azure.
        subscription_id(str, Optional): Subscription credentials which uniquely identify Microsoft Azure subscription. The subscription ID forms part of the URI for every service call.


    Returns:
        Dict

    Examples:
        .. code-block:: sls

            my-disk:
              azure.compute.disks.present:
                - resource_group_name: resource-group-name
                - disk_name: disk-1
                - location: westus
                - creation_data:
                    create_option: FromImage
                    image_reference:
                      id: /Subscriptions/sub-id/Providers/Microsoft.Compute/Locations/westus/Publishers/Canonical/ArtifactTypes/VMImage/Offers/UbuntuServer/Skus/16.04-LTS/Versions/16.04.202109280
    """
    path_properties = {
        "subscription_id": subscription_id,
        "resource_group_name": resource_group_name,
        "disk_name": disk_name,
    }
    query_properties = {}
    body_properties = {
        "location": location,
        "tags": tags,
        "sku": sku,
        "zones": zones,
        "extended_location": extended_location,
        "os_type": os_type,
        "hyper_v_generation": hyper_v_generation,
        "creation_data": creation_data,
        "disk_size_gb": disk_size_gb,
        "encryption_settings_collection": encryption_settings_collection,
        "disk_iops_read_write": disk_iops_read_write,
        "disk_mbps_read_write": disk_mbps_read_write,
        "disk_iops_read_only": disk_iops_read_only,
        "disk_mbps_read_only": disk_mbps_read_only,
        "encryption": encryption,
        "max_shares": max_shares,
        "network_access_policy": network_access_policy,
        "disk_access_id": disk_access_id,
        "tier": tier,
        "bursting_enabled": bursting_enabled,
        "security_profile": security_profile,
        "public_network_access": public_network_access,
        "data_access_auth_mode": data_access_auth_mode,
    }
    return await hub.tool.azure.generic.run_present(
        ctx,
        "azure.compute.disks",
        name,
        resource_id,
        path_properties,
        query_properties,
        body_properties,
    )


async def absent(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    resource_group_name: str = None,
    disk_name: str = None,
    subscription_id: str = None,
) -> Dict:
    r"""Delete a Disk.

    Args:
        name(str): The identifier for this state.
        disk_name(str): The name of the disk.
        resource_group_name(str): The name of the resource group.
        subscription_id(str): Subscription Unique id.
        resource_id(str, Optional): Disk resource id on Azure.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.compute.disks.absent:
                - name: my-disk
                - resource_group_name: my-resource-group
                - disk_name: my-disk
                - subscription_id: my-subscription
    """
    return hub.tool.azure.result_utils.absent_implemented_through_wrapper_result(
        "azure.compute.disks", name
    )


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Disks under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.compute.disks
    """
    result = {}
    ret_list = await hub.exec.azure.compute.disks.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe compute disks {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.compute.disks.present": [
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
