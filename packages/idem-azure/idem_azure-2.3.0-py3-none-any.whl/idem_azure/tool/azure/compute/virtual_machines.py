import copy
from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List

# TODO: add generic logic which takes matching values by default,
#   also between snake and camel case conversions
#   needs override only for special cases - renamings
PRESENT_TO_RAW_MAP = {
    "properties": {
        "licenseType": "license_type",
        "diagnosticsProfile": {
            "bootDiagnostics": {
                "enabled": "boot_diagnostics.enabled",
                "storageUri": "boot_diagnostics.storage_uri",
            }
        },
        "availabilitySet": {"id": "availability_set_id"},
        "osProfile": {
            "adminUsername": "os_profile.admin_username",
            "adminPassword": "os_profile.admin_password",
            "computerName": "os_profile.computer_name",
            "customData": "os_profile.custom_data",
            "linuxConfiguration": {
                "ssh": {
                    "publicKeys": [
                        {
                            "$list_refs": [
                                "os_profile.linux_configuration.ssh_public_keys"
                            ],
                            "keyData": "os_profile.linux_configuration.ssh_public_keys.key_data",
                            "path": "os_profile.linux_configuration.ssh_public_keys.path",
                        }
                    ]
                },
                "provisionVMAgent": "os_profile.linux_configuration.provision_vm_agent",
                "enableVMAgentPlatformUpdates": "os_profile.linux_configuration.enable_vm_agent_platform_updates",
                "disablePasswordAuthentication": "os_profile.linux_configuration.disable_password_authentication",
            },
            "windowsConfiguration": {
                "provisionVMAgent": "os_profile.windows_configuration.provision_vm_agent",
                "enableVMAgentPlatformUpdates": "os_profile.windows_configuration.enable_vm_agent_platform_updates",
                "enableAutomaticUpdates": "os_profile.windows_configuration.enable_automatic_updates",
                "timeZone": "os_profile.windows_configuration.time_zone",
            },
        },
        "extensionsTimeBudget": "extensions_time_budget",
    },
    "plan": {
        "name": "plan.name",
        "product": "plan.product",
        "promotionCode": "plan.promotion_code",
        "publisher": "plan.publisher",
    },
}

# TODO: add generic logic for converting one map to the other
RAW_TO_PRESENT_MAP = {
    "license_type": "properties.licenseType",
    "boot_diagnostics": {
        "enabled": "properties.diagnosticsProfile.bootDiagnostics.enabled",
        "storage_uri": "properties.diagnosticsProfile.bootDiagnostics.storageUri",
    },
    "plan": {
        "name": "plan.name",
        "product": "plan.product",
        "promotion_code": "plan.promotionCode",
        "publisher": "plan.publisher",
    },
    "availability_set_id": "properties.availabilitySet.id",
    "os_profile": {
        "computer_name": "properties.osProfile.computerName",
        "admin_username": "properties.osProfile.adminUsername",
        "admin_password": "properties.osProfile.adminPassword",
        "custom_data": "properties.osProfile.customData",
        "linux_configuration": {
            "ssh_public_keys": [
                {
                    "$list_refs": [
                        "properties.osProfile.linuxConfiguration.ssh.publicKeys"
                    ],
                    "key_data": "properties.osProfile.linuxConfiguration.ssh.publicKeys.keyData",
                    "path": "properties.osProfile.linuxConfiguration.ssh.publicKeys.path",
                }
            ],
            "provision_vm_agent": "properties.osProfile.linuxConfiguration.provisionVMAgent",
            "enable_vm_agent_platform_updates": "properties.osProfile.linuxConfiguration.enableVMAgentPlatformUpdates",
            "disable_password_authentication": "properties.osProfile.linuxConfiguration.disablePasswordAuthentication",
        },
        "windows_configuration": {
            "provision_vm_agent": "properties.osProfile.windowsConfiguration.provisionVMAgent",
            "enable_vm_agent_platform_updates": "properties.osProfile.windowsConfiguration.enableVMAgentPlatformUpdates",
            "enable_automatic_updates": "properties.osProfile.windowsConfiguration.enableAutomaticUpdates",
            "time_zone": "properties.osProfile.windowsConfiguration.timeZone",
        },
    },
    "extensions_time_budget": "properties.extensionsTimeBudget",
}


def convert_present_to_raw_virtual_machine(
    hub,
    location: str = None,
    network_interface_ids: List[str] = None,
    os_profile: Dict[str, Any] = None,
    storage_os_disk: Dict[str, Any] = None,
    virtual_machine_size: str = None,
    storage_image_reference: Dict[str, Any] = None,
    storage_data_disks: List[Dict[str, Any]] = None,
    tags: Dict = None,
    plan: Dict[str, str] = None,
    availability_set_id: str = None,
    license_type: str = None,
    boot_diagnostics: Dict[str, Any] = None,
    extensions_time_budget: str = None,
    **kwargs,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        location(str, Optional): Resource location. Changing this forces a new resource to be created.
        network_interface_ids(List[str], Optional): A list of Network Interface IDs which should be associated with the Virtual Machine.
        os_profile(Dict[str, Any], Optional): Specifies the operating system settings used while creating the virtual machine.
        storage_os_disk(Dict[str, Any], Optional): Specifies information about the operating system disk used by the virtual machine.
        virtual_machine_size(str, Optional): Specifies the size of the Virtual Machine.
        storage_image_reference(Dict[str, Any], Optional): Specifies information about the image to use. Eg- platform images, marketplace images.
        storage_data_disks(List[Dict[str, Any]], Optional): List of Data disks attached/added to a VM.
        tags(Dict, Optional): Resource tags.
        plan(Dict[str, str], Optional): Specifies information about the marketplace image used to create the virtual machine.
        availability_set_id(str, Optional): Specifies id of the availability set that the virtual machine should be assigned to.
        license_type(str, Optional): Specifies that the image or disk that is being used was licensed on-premises.
        boot_diagnostics(Dict[str, Any]): Specifies the boot diagnostic settings state.
        extensions_time_budget(str, Optional): Specifies the time alloted for all extensions to start.

    Returns:
        A Dict in the format of an Azure PUT operation payload.
    """

    expected_ignored = {
        "name",
        "resource_id",
        "resource_group_name",
        "virtual_machine_name",
        "subscription_id",
    }
    if kwargs and kwargs.keys() - expected_ignored:
        hub.log.warning(f"Ignored VM properties: {kwargs.keys() - expected_ignored}!")

    generic_present_state = {
        k: v for (k, v) in locals().items() if k in RAW_TO_PRESENT_MAP.keys()
    }

    generic_raw_state = hub.tool.azure.generic.convert_state_format(
        generic_present_state,
        PRESENT_TO_RAW_MAP,
    )

    payload = generic_raw_state
    if location is not None:
        payload["location"] = location

    if virtual_machine_size is not None:
        hub.tool.azure.utils.dict_add_nested_key_value_pair(
            payload, ["properties", "hardwareProfile", "vmSize"], virtual_machine_size
        )

    if network_interface_ids is not None:
        network_interface_ids_payload = {
            "networkInterfaces": convert_present_to_raw_network_interfaces(
                network_interface_ids
            )
        }
        hub.tool.azure.utils.dict_add_nested_key_value_pair(
            payload, ["properties", "networkProfile"], network_interface_ids_payload
        )

    if storage_image_reference is not None:
        storage_image_reference_payload = hub.tool.azure.compute.virtual_machines.convert_present_to_raw_image_reference(
            storage_image_reference
        )
        hub.tool.azure.utils.dict_add_nested_key_value_pair(
            payload,
            ["properties", "storageProfile", "imageReference"],
            storage_image_reference_payload,
        )

    if storage_os_disk is not None:
        os_disk_payload = convert_present_to_raw_os_disk(storage_os_disk)
        hub.tool.azure.utils.dict_add_nested_key_value_pair(
            payload, ["properties", "storageProfile", "osDisk"], os_disk_payload
        )

    if storage_data_disks is not None:
        data_disks_payload = convert_present_to_raw_data_disks(storage_data_disks)
        hub.tool.azure.utils.dict_add_nested_key_value_pair(
            payload, ["properties", "storageProfile", "dataDisks"], data_disks_payload
        )

    if tags is not None:
        payload["tags"] = tags

    return payload


def convert_raw_virtual_machine_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    virtual_machine_name: str,
    resource_id: str,
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
        virtual_machine_name: Azure Virtual Machine resource name.
        resource_id: Azure Virtual Machine resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
      A Dict that contains the parameters that match the present function's input format.
    """

    generic_present_state = hub.tool.azure.generic.convert_state_format(
        resource,
        RAW_TO_PRESENT_MAP,
    )

    resource_translated = {
        **generic_present_state,
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "virtual_machine_name": virtual_machine_name,
        "location": resource.get("location"),
        "subscription_id": subscription_id,
    }
    properties = resource.get("properties")
    if properties:
        if properties.get("hardwareProfile") is not None:
            resource_translated["virtual_machine_size"] = properties.get(
                "hardwareProfile"
            ).get("vmSize")

        if properties.get("networkProfile") is not None:
            if properties.get("networkProfile").get("networkInterfaces") is not None:
                network_profile_payload = convert_raw_to_present_network_interface(
                    network_interfaces=properties.get("networkProfile").get(
                        "networkInterfaces"
                    )
                )
                resource_translated["network_interface_ids"] = network_profile_payload

        if properties.get("storageProfile") is not None:
            storage_profile_properties = properties.get("storageProfile")
            if storage_profile_properties.get("imageReference") is not None:
                image_reference_payload = convert_raw_to_present_image_reference(
                    image_reference=storage_profile_properties.get("imageReference")
                )
                resource_translated["storage_image_reference"] = image_reference_payload
            if storage_profile_properties.get("osDisk") is not None:
                os_disk_payload = convert_raw_to_present_os_disk(
                    os_disk=storage_profile_properties.get("osDisk")
                )
                resource_translated["storage_os_disk"] = os_disk_payload
            if storage_profile_properties.get("dataDisks") is not None:
                data_disk_payload = convert_raw_to_present_data_disks(
                    data_disks=storage_profile_properties.get("dataDisks")
                )
                resource_translated["storage_data_disks"] = data_disk_payload

        if properties.get("instanceView"):
            statuses = properties["instanceView"].get("statuses", [])
            power_state_status = next(
                (status for status in statuses if "PowerState" in status["code"]), None
            )
            if power_state_status is not None:
                status = power_state_status["code"].replace("PowerState/", "")
                resource_translated["status"] = status
    if "tags" in resource:
        resource_translated["tags"] = resource.get("tags")

    return resource_translated


def update_virtual_machine_payload(
    hub,
    existing_payload: Dict[str, Any],
    old_values_present: Dict[str, Any],
    new_values_present: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate an updated payload, which can be used by
    PUT operation to update a resource on Azure.

    Args:
        hub: The redistributed pop central hub.
        existing_payload: The existing resource state in raw format. This is usually a GET operation response.
        old_values: The existing resource state in present format
        new_values: A dictionary of desired state values in present format. If any property's value is None,
        this property will be ignored. This is to match the behavior when a present() input is a None, Idem does not
        do an update.

    Returns:
        A result Dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages list.
    """
    result = {"result": True, "ret": None, "comment": []}

    new_values = hub.tool.azure.utils.cleanup_none_values(new_values_present)

    old_values = hub.tool.azure.utils.cleanup_none_values(old_values_present)

    generic_update_payload = (
        hub.tool.azure.generic.compute_update_payload_for_key_subset(
            old_values, new_values, key_subset=RAW_TO_PRESENT_MAP.keys()
        )
    )
    need_update = bool(generic_update_payload)

    for old_prop_name, old_prop_value in old_values.items():
        if old_prop_name not in generic_update_payload:
            generic_update_payload[old_prop_name] = copy.deepcopy(old_prop_value)

    new_payload = (
        hub.tool.azure.compute.virtual_machines.convert_present_to_raw_virtual_machine(
            **generic_update_payload
        )
    )

    existing_properties = existing_payload.get("properties", {})

    if new_values.get("virtual_machine_size") is not None:
        if (
            (existing_properties.get("hardwareProfile") is not None)
            and (existing_properties.get("hardwareProfile").get("vmSize") is not None)
            and (
                existing_properties.get("hardwareProfile").get("vmSize")
                != new_values.get("virtual_machine_size")
            )
        ):
            new_virtual_machine_size = new_values.get("virtual_machine_size")
            hub.tool.azure.utils.dict_add_nested_key_value_pair(
                new_payload,
                ["properties", "hardwareProfile", "vmSize"],
                new_virtual_machine_size,
            )
            need_update = True

    if new_values.get("network_interface_ids"):
        if (
            (existing_properties.get("networkProfile") is not None)
            and (
                existing_properties.get("networkProfile").get("networkInterfaces")
                is not None
            )
            and (
                compare_network_interface_payload(
                    existing_properties.get("networkProfile").get("networkInterfaces"),
                    new_values.get("network_interface_ids"),
                )
            )
        ):
            network_profile_payload = {
                "networkInterfaces": convert_present_to_raw_network_interfaces(
                    network_interface_ids=new_values.get("network_interface_ids")
                )
            }
            hub.tool.azure.utils.dict_add_nested_key_value_pair(
                new_payload, ["properties", "networkProfile"], network_profile_payload
            )
            need_update = True
    if new_values.get("storage_data_disks") is not None:
        if (
            (existing_properties.get("storageProfile") is not None)
            and (existing_properties.get("storageProfile").get("dataDisks") is not None)
            and (
                compare_storage_data_disks_payload(
                    existing_properties.get("storageProfile").get("dataDisks"),
                    new_values.get("storage_data_disks"),
                )
            )
        ):
            new_data_disks = convert_present_to_raw_data_disks(
                data_disks=merge_data_disks_payloads(
                    convert_raw_to_present_data_disks(
                        existing_properties.get("storageProfile").get("dataDisks")
                    ),
                    new_values.get("storage_data_disks"),
                )
            )
            hub.tool.azure.utils.dict_add_nested_key_value_pair(
                new_payload,
                ["properties", "storageProfile", "dataDisks"],
                new_data_disks,
            )
            need_update = True
    if new_values.get("storage_os_disk") is not None:
        if (
            (existing_properties.get("storageProfile") is not None)
            and (existing_properties.get("storageProfile").get("osDisk") is not None)
            and (
                compare_storage_os_disk_payload(
                    existing_properties.get("storageProfile").get("osDisk"),
                    new_values.get("storage_os_disk"),
                )
            )
        ):
            new_os_disk = convert_present_to_raw_os_disk(
                os_disk=merge_dictionary_payloads(
                    convert_raw_to_present_os_disk(
                        existing_properties.get("storageProfile").get("osDisk")
                    ),
                    new_values.get("storage_os_disk"),
                )
            )
            hub.tool.azure.utils.dict_add_nested_key_value_pair(
                new_payload, ["properties", "storageProfile", "osDisk"], new_os_disk
            )
            need_update = True
    if new_values.get("storage_image_reference") is not None:
        if (
            (existing_properties.get("storageProfile") is not None)
            and (
                existing_properties.get("storageProfile").get("imageReference")
                is not None
            )
            and (
                compare_storage_image_reference_payload(
                    existing_properties.get("storageProfile").get("imageReference"),
                    new_values.get("storage_image_reference"),
                )
            )
        ):
            new_image_ref = hub.tool.azure.compute.virtual_machines.convert_present_to_raw_image_reference(
                storage_image_reference=merge_dictionary_payloads(
                    convert_raw_to_present_image_reference(
                        existing_properties.get("storageProfile").get("imageReference")
                    ),
                    new_values.get("storage_image_reference"),
                )
            )
            hub.tool.azure.utils.dict_add_nested_key_value_pair(
                new_payload,
                ["properties", "storageProfile", "imageReference"],
                new_image_ref,
            )
            need_update = True

    if (new_values.get("tags") is not None) and (
        existing_payload.get("tags") != new_values.get("tags")
    ):
        new_payload["tags"] = new_values.get("tags")
        need_update = True

    if need_update:
        result["ret"] = new_payload
    return result


def convert_present_to_raw_network_interfaces(network_interface_ids: List[str]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        network_interface_ids(List[str]) : List of Network Interface Ids

    Returns:
        Network Interface Ids List[Dict[str, Any]] in the format of an Azure PUT operation payload.
    """
    network_interface_id_counter = 0
    network_interfaces_list: List = []
    for network_interface_id in network_interface_ids:
        network_interfaces_payload = {"id": network_interface_id}
        primary_network_payload = {}
        if network_interface_id_counter == 0:
            primary_network_payload["primary"] = True
        else:
            primary_network_payload["primary"] = False
        network_interfaces_payload["properties"] = primary_network_payload
        network_interfaces_list.append(network_interfaces_payload)
        network_interface_id_counter = network_interface_id_counter + 1
    return network_interfaces_list


def convert_present_to_raw_image_reference(
    hub, storage_image_reference: Dict[str, Any]
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        storage_image_reference(Dict(str, Any)) : Specifies information about the image to use in VM creation/update

    Returns:
        Storage Image Reference Dict[str,any] in the format of an Azure PUT operation payload.
    """
    storage_image_reference_payload = {
        "publisher": storage_image_reference.get("image_publisher"),
        "offer": storage_image_reference.get("image_offer"),
        "sku": storage_image_reference.get("image_sku"),
        "version": storage_image_reference.get("image_version"),
        "id": storage_image_reference.get("image_id"),
        "sharedGalleryImageId": storage_image_reference.get("shared_gallery_image_id"),
        "communityGalleryImageId": storage_image_reference.get(
            "community_gallery_image_id"
        ),
    }
    return hub.tool.azure.utils.cleanup_none_values(storage_image_reference_payload)


def convert_present_to_raw_os_disk(os_disk: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        os_disk(Dict(str, Any)) : Specifies information about the operating system disk used by the virtual machine.

    Returns:
        OS Disk Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    os_disk_payload = {
        "name": os_disk.get("disk_name"),
        "diskSizeGB": os_disk.get("disk_size_in_GB"),
        "caching": os_disk.get("disk_caching"),
        "createOption": os_disk.get("disk_create_option"),
        "deleteOption": os_disk.get("disk_delete_option"),
        "managedDisk": {
            "id": os_disk.get("disk_id"),
            "storageAccountType": os_disk.get("storage_account_type"),
        },
    }
    if os_disk.get("disk_image_vhd_uri") is not None:
        os_disk_payload["image"] = {"uri": os_disk.get("disk_image_vhd_uri")}
    if os_disk.get("disk_os_type") is not None:
        os_disk_payload["osType"] = os_disk.get("disk_os_type")

    if os_disk.get("disk_vhd_uri") is not None:
        os_disk_payload["vhd"] = {"uri": os_disk.get("disk_vhd_uri")}

    if os_disk.get("write_accelerator_enabled") is not None:
        os_disk_payload["writeAcceleratorEnabled"] = os_disk.get(
            "write_accelerator_enabled"
        )

    return os_disk_payload


def convert_present_to_raw_data_disks(data_disks: List[Dict[str, Any]]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        data_disks(List[Dict[str, Any]] : List of Data Disk payload for VM

    Returns:
        List of Data Disk payload List[Dict[str, Any]] in the format of an Azure PUT operation payload.
    """
    data_disks_list: List = []
    for data_disk in data_disks:
        data_disks_payload = {
            "name": data_disk.get("disk_name"),
            "diskSizeGB": data_disk.get("disk_size_in_GB"),
            "lun": data_disk.get("disk_logical_unit_number"),
            "caching": data_disk.get("disk_caching"),
            "createOption": data_disk.get("disk_create_option"),
            "deleteOption": data_disk.get("disk_delete_option"),
            "managedDisk": {
                "id": data_disk.get("disk_id"),
                "storageAccountType": data_disk.get("storage_account_type"),
            },
        }
        data_disks_list.append(data_disks_payload)
    return data_disks_list


def convert_raw_to_present_network_interface(network_interfaces: List[Dict[str, Any]]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        network_interfaces(List[Dict], optional): Resource List of Network Interfaces in a virtual machine resource.

    Returns:
         A Network Interface Id List that contains the parameters that match respective present function's input format.
    """
    present_network_interfaces: List = []
    for network_interface in network_interfaces:
        present_network_interfaces.append(network_interface.get("id"))
    return present_network_interfaces


def convert_raw_to_present_image_reference(image_reference: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        image_reference(Dict, optional): Image Reference payload in a virtual machine resource.

    Returns:
         Image Reference payload contains the parameters that match respective present function's input format.
    """
    image_reference_payload = {
        "image_sku": image_reference.get("sku"),
        "image_publisher": image_reference.get("publisher"),
        "image_version": image_reference.get("version"),
        "image_offer": image_reference.get("offer"),
        "image_id": image_reference.get("id"),
        "shared_gallery_image_id": image_reference.get("sharedGalleryImageId"),
        "community_gallery_image_id": image_reference.get("communityGalleryImageId"),
    }
    return image_reference_payload


def convert_raw_to_present_os_disk(os_disk: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        os_disk(Dict, optional): OS Disk payload in a virtual machine resource.

    Returns:
         OS Disk payload that contains the parameters that match respective present function's input format.
    """
    os_disk_payload = {
        "disk_name": os_disk.get("name"),
        "disk_caching": os_disk.get("caching"),
    }
    if os_disk.get("diskSizeGB") is not None:
        os_disk_payload["disk_size_in_GB"] = os_disk.get("diskSizeGB")
    if (
        os_disk.get("managedDisk") is not None
        and os_disk.get("managedDisk").get("storageAccountType") is not None
    ):
        os_disk_payload["storage_account_type"] = os_disk.get("managedDisk").get(
            "storageAccountType"
        )
    if (
        os_disk.get("managedDisk") is not None
        and os_disk.get("managedDisk").get("id") is not None
    ):
        os_disk_payload["disk_id"] = os_disk.get("managedDisk").get("id")
    if os_disk.get("createOption") is not None:
        os_disk_payload["disk_create_option"] = os_disk.get("createOption")
    if os_disk.get("deleteOption") is not None:
        os_disk_payload["disk_delete_option"] = os_disk.get("deleteOption")

    os_disk_image = os_disk.get("image")
    if os_disk_image is not None and os_disk_image.get("uri") is not None:
        os_disk_payload["disk_image_vhd_uri"] = os_disk_image["uri"]
    if os_disk.get("osType") is not None:
        os_disk_payload["disk_os_type"] = os_disk.get("osType")

    os_disk_vhd = os_disk.get("vhd")
    if os_disk_vhd is not None and os_disk_vhd.get("uri") is not None:
        os_disk_payload["disk_vhd_uri"] = os_disk_vhd["uri"]
    if os_disk.get("writeAcceleratorEnabled") is not None:
        os_disk_payload["write_accelerator_enabled"] = os_disk.get(
            "writeAcceleratorEnabled"
        )
    return os_disk_payload


def convert_raw_to_present_data_disks(data_disks: List[Dict[str, Any]]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        data_disks(List[Dict], optional): Resource List of Data Disks in a virtual machine resource.

    Returns:
         A Data Disk List that contains the parameters that match respective present function's input format.
    """
    present_data_disks_payload: List = []
    for data_disk in data_disks:
        data_disk_payload = {
            "disk_name": data_disk.get("name"),
            "disk_logical_unit_number": data_disk.get("lun"),
            "disk_caching": data_disk.get("caching"),
        }
        if data_disk.get("diskSizeGB") is not None:
            data_disk_payload["disk_size_in_GB"] = data_disk.get("diskSizeGB")
        if (
            data_disk.get("managedDisk") is not None
            and data_disk.get("managedDisk").get("storageAccountType") is not None
        ):
            data_disk_payload["storage_account_type"] = data_disk.get(
                "managedDisk"
            ).get("storageAccountType")
        if (
            data_disk.get("managedDisk") is not None
            and data_disk.get("managedDisk").get("id") is not None
        ):
            data_disk_payload["disk_id"] = data_disk.get("managedDisk").get("id")
        if data_disk.get("createOption") is not None:
            data_disk_payload["disk_create_option"] = data_disk.get("createOption")
        if data_disk.get("deleteOption") is not None:
            data_disk_payload["disk_delete_option"] = data_disk.get("deleteOption")
        present_data_disks_payload.append(data_disk_payload)
    return present_data_disks_payload


def compare_network_interface_payload(
    existing_network_interface_list: List[Dict[str, Any]],
    network_interface_ids: List[str],
):
    """
    Compares network interface payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_network_interface_list(List[Dict]): Existing Network Interface payload
        network_interface_ids(List[str]): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    if len(network_interface_ids) != len(existing_network_interface_list):
        return True
    existing_network_interface_id_list = []
    for existing_network_interface in existing_network_interface_list:
        existing_network_interface_id_list.append(existing_network_interface.get("id"))
    return set(existing_network_interface_id_list) != set(network_interface_ids)


def compare_storage_os_disk_payload(
    existing_storage_os_disk_payload: Dict[str, Any],
    new_storage_os_disk: Dict[str, Any],
):
    """
    Compares OS Disk payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_storage_os_disk_payload[Dict]: Existing Storage OS Disk payload
        new_storage_os_disk[Dict]: Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    os_disk_present_converted_payload = convert_raw_to_present_os_disk(
        existing_storage_os_disk_payload
    )
    return compare_update_dict_payload(
        os_disk_present_converted_payload, new_storage_os_disk
    )


def compare_storage_data_disks_payload(
    existing_storage_data_disks_payload: List[Dict[str, Any]],
    new_storage_data_disks: List[Dict[str, Any]],
):
    """
    Compares Data Disks payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_storage_data_disks_payload(List[Dict]): Existing Storage Data Disk payload
        new_storage_data_disks(List[str]): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    data_disks_present_converted_payload = convert_raw_to_present_data_disks(
        existing_storage_data_disks_payload
    )
    if len(data_disks_present_converted_payload) != len(new_storage_data_disks):
        return True
    existing_payload_map = {}
    for element in data_disks_present_converted_payload:
        existing_payload_map[element.get("disk_name")] = element

    return compare_update_dict_list_payload(
        existing_payload_map, new_storage_data_disks
    )


def compare_storage_image_reference_payload(
    existing_storage_image_reference_payload: Dict[str, Any],
    new_storage_image_reference: Dict[str, Any],
):
    """
    Compares Storage Image Reference payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_storage_image_reference_payload(Dict): Existing Storage Image Reference payload
        new_storage_image_reference(Dict): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    storage_image_reference_present_converted_payload = (
        convert_raw_to_present_image_reference(existing_storage_image_reference_payload)
    )
    return compare_update_dict_payload(
        storage_image_reference_present_converted_payload, new_storage_image_reference
    )


def compare_update_dict_payload(
    existing_payload: Dict[str, Any], update_payload: Dict[str, Any]
):
    """
    Compares the payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_payload(Dict): Existing payload
        update_payload(Dict): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    for parameter in update_payload:
        if parameter in existing_payload:
            if update_payload.get(parameter) != existing_payload.get(parameter):
                return True
        else:
            return True
    return False


def compare_update_dict_list_payload(
    existing_payload_map: Dict[str, Any], update_payload: List[Dict[str, Any]]
):
    """
    Compares the payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_payload_map(Dict): Existing payload Map
        update_payload(List[Dict]): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    for update_element in update_payload:
        disk_name = update_element.get("disk_name")
        if disk_name in existing_payload_map:
            if compare_update_dict_payload(
                existing_payload_map.get(disk_name), update_element
            ):
                return True
        else:
            return True
    return False


def merge_dictionary_payloads(
    existing_payload: Dict[str, Any], update_payload: Dict[str, Any]
):
    """
    Merge the input payload with the payload from Azure Get Response
    Returns the merged payload

    Args:
        existing_payload(Dict): Existing payload From Azure Get API
        update_payload(Dict): Present value which will be given as input

    Returns:
        A Dict of the merged Payload
    """
    existing_payload_copy = copy.deepcopy(existing_payload)
    for update_element_key in update_payload:
        if update_payload.get(update_element_key) is not None:
            existing_payload_copy[update_element_key] = update_payload.get(
                update_element_key
            )
    return existing_payload_copy


def merge_data_disks_payloads(
    existing_payload: List[Dict[str, Any]], update_payload: List[Dict[str, Any]]
):
    """
    Merge the input payload with the payload from Azure Get Response for Data Disks
    Returns the merged Data Disk payload

    Args:
        existing_payload(Dict): Existing payload Map
        update_payload(Dict): Present value which will be given as input

    Returns:
        A Dict of the merged Data Disks Payload
    """
    existing_payload_map = {}
    existing_merged_payload = []
    for element in existing_payload:
        existing_payload_map[element.get("disk_name")] = element
    for update_element in update_payload:
        disk_name = update_element.get("disk_name")
        if disk_name in existing_payload_map:
            # Merge Data
            existing_merged_payload.append(
                merge_dictionary_payloads(
                    existing_payload_map.get(disk_name), update_element
                )
            )
        else:
            # Keep new input data
            existing_merged_payload.append(update_element)
    return existing_merged_payload


def convert_raw_to_present_state(hub, raw_state):
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "virtualMachines": "virtual_machine_name",
        }
    )
    resource_id = raw_state["id"]
    uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
        resource_id, uri_parameters
    )

    return (
        hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
            resource=raw_state,
            resource_id=resource_id,
            idem_resource_name=raw_state["name"]
            if "name" in raw_state
            else resource_id,
            **uri_parameter_values,
        )
    )


def convert_present_to_raw_state(hub, present_state):
    return (
        hub.tool.azure.compute.virtual_machines.convert_present_to_raw_virtual_machine(
            location=present_state["location"],
            network_interface_ids=present_state["network_interface_ids"],
            os_profile=present_state["os_profile"],
            storage_os_disk=present_state["storage_os_disk"],
            virtual_machine_size=present_state["virtual_machine_size"],
            storage_image_reference=present_state["storage_image_reference"],
            storage_data_disks=present_state["storage_data_disks"],
            tags=present_state["tags"],
            plan=present_state["plan"],
            availability_set_id=present_state["availability_set_id"],
            license_type=present_state["license_type"],
        )
    )
