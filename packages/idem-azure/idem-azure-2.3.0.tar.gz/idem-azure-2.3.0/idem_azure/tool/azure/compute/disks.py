"""Tool module for managing Compute Disks."""

RAW_TO_PRESENT_MAP = {
    "subscription_id": "subscriptionId",
    "resource_group_name": "resourceGroupName",
    "disk_name": "diskName",
    "location": "location",
    "creation_data": {
        "create_option": "properties.creationData.createOption",
        "gallery_image_reference": {
            "id": "properties.creationData.galleryImageReference.id",
            "lun": "properties.creationData.galleryImageReference.lun",
        },
        "image_reference": {
            "id": "properties.creationData.imageReference.id",
            "lun": "properties.creationData.imageReference.lun",
        },
        "logical_sector_size": "properties.creationData.logicalSectorSize",
        "security_data_uri": "properties.creationData.securityDataUri",
        "source_resource_id": "properties.creationData.sourceResourceId",
        "source_unique_id": "properties.creationData.sourceUniqueId",
        "source_uri": "properties.creationData.sourceUri",
        "storage_account_id": "properties.creationData.storageAccountId",
        "upload_size_bytes": "properties.creationData.uploadSizeBytes",
    },
    "extended_location": {
        "name": "extendedLocation.name",
        "type": "extendedLocation.type",
    },
    "bursting_enabled": "properties.burstingEnabled",
    "data_access_auth_mode": "properties.dataAccessAuthMode",
    "disk_access_id": "properties.diskAccessId",
    "disk_iops_read_only": "properties.diskIOPSReadOnly",
    "disk_iops_read_write": "properties.diskIOPSReadWrite",
    "disk_mbps_read_only": "properties.diskMBpsReadOnly",
    "disk_mbps_read_write": "properties.diskMBpsReadWrite",
    "disk_size_gb": "properties.diskSizeGB",
    "encryption": {
        "disk_encryption_set_id": "properties.encryption.diskEncryptionSetId",
        "type": "properties.encryption.type",
    },
    "encryption_settings_collection": {
        "enabled": "properties.encryptionSettingsCollection.enabled",
        "encryption_settings": {
            "disk_encryption_key": {
                "secret_url": "properties.encryptionSettingsCollection.encryptionSettings.diskEncryptionKey.secretUrl",
                "source_vault": {
                    "vm_uri": "properties.encryptionSettingsCollection.encryptionSettings.diskEncryptionKey.sourceVault.vmUri"
                },
            },
            "key_encryption_key": {
                "key_url": "properties.encryptionSettingsCollection.encryptionSettings.keyEncryptionKey.keyUrl",
                "source_vault": {
                    "vm_uri": "properties.encryptionSettingsCollection.encryptionSettings.keyEncryptionKey.sourceVault.vmUri"
                },
            },
        },
        "encryption_settings_version": "properties.encryptionSettingsCollection.encryptionSettingsVersion",
    },
    "hyper_v_generation": "properties.hyperVGeneration",
    "max_shares": "properties.maxShares",
    "network_access_policy": "properties.networkAccessPolicies",
    "os_type": "properties.osType",
    "public_network_access": "properties.publicNetworkAccess",
    "security_profile": {
        "secure_vm_disk_encryption_set_id": "properties.securityProfile.secureVMDiskEncryptionSetId",
        "security_type": "properties.securityProfile.securityType",
    },
    "tier": "properties.tier",
    "sku": {"name": "sku.name", "tier": "sku.tier"},
    "tags": "tags",
    "zones": "zones",
}

PRESENT_TO_RAW_MAP = {
    "subscriptionId": "subscription_id",
    "resourceGroupName": "resource_group_name",
    "diskName": "disk_name",
    "location": "location",
    "properties": {
        "creationData": {
            "createOption": "creation_data.create_option",
            "galleryImageReference": {
                "id": "creation_data.gallery_image_reference.id",
                "lun": "creation_data.gallery_image_reference.lun",
            },
            "imageReference": {
                "id": "creation_data.image_reference.id",
                "lun": "creation_data.image_reference.lun",
            },
            "logicalSectorSize": "creation_data.logical_sector_size",
            "securityDataUri": "creation_data.security_data_uri",
            "sourceResourceId": "creation_data.source_resource_id",
            "sourceUniqueId": "creation_data.source_unique_id",
            "sourceUri": "creation_data.source_uri",
            "storageAccountId": "creation_data.storage_account_id",
            "uploadSizeBytes": "creation_data.upload_size_bytes",
        },
        "burstingEnabled": "bursting_enabled",
        "dataAccessAuthMode": "data_access_auth_mode",
        "diskAccessId": "disk_access_id",
        "diskIOPSReadOnly": "disk_iops_read_only",
        "diskIOPSReadWrite": "disk_iops_read_write",
        "diskMBpsReadOnly": "disk_mbps_read_only",
        "diskMBpsReadWrite": "disk_mbps_read_write",
        "diskSizeGB": "disk_size_gb",
        "encryption": {
            "diskEncryptionSetId": "encryption.disk_encryption_set_id",
            "type": "encryption.type",
        },
        "encryptionSettingsCollection": {
            "enabled": "encryptionS_settings_collection.enabled",
            "encryptionSettings": {
                "diskEncryptionKey": {
                    "secretUrl": "encryption_settings_collection.encryption_settings.disk_encryption_key.secret_url",
                    "sourceVault": {
                        "vmUri": "encryption_settings_collection.encryption_settings.disk_encryption_key.source_vault.vm_uri"
                    },
                },
                "keyEncryptionKey": {
                    "keyUrl": "encryption_settings_collection.encryption_settings.key_encryption_key.key_url",
                    "sourceVault": {
                        "vmUri": "encryption_settings_collection.encryption_settings.key_encryption_key.source_vault.vm_uri"
                    },
                },
            },
            "encryptionSettingsVersion": "encryption_settings_collection.encryption_settings_version",
        },
        "hyperVGeneration": "hyper_v_generation",
        "maxShares": "max_shares",
        "networkAccessPolicy": "network_access_policies",
        "osType": "os_type",
        "publicNetworkAccess": "public_network_access",
        "securityProfile": {
            "secureVMDiskEncryptionSetId": "security_profile.secure_vm_disk_encryption_set_id",
            "securityType": "security_profile.security_type",
        },
        "tier": "tier",
    },
    "extendedLocation": {
        "name": "extended_location.name",
        "type": "extended_location.type",
    },
    "sku": {"name": "sku.name", "tier": "sku.tier"},
    "tags": "tags",
    "zones": "zones",
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
