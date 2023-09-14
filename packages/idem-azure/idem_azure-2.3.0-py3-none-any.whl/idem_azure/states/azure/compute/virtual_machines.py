"""State module for managing Compute Virtual Machine."""
import copy
from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]
__reconcile_wait__ = {"static": {"wait_in_seconds": 10}}


async def present(
    hub,
    ctx,
    name: str,
    location: str,
    network_interface_ids: List[str],
    os_profile: make_dataclass(
        "OsProfile",
        [
            ("computer_name", str),
            ("admin_username", str),
            ("admin_password", str, field(default=None)),
            ("custom_data", str, field(default=None)),
            (
                "linux_configuration",
                make_dataclass(
                    "LinuxConfiguration",
                    [
                        (
                            "ssh_public_keys",
                            List[
                                make_dataclass(
                                    "SshPublicKey",
                                    [
                                        ("key_data", str, field(default=None)),
                                        ("path", str, field(default=None)),
                                    ],
                                )
                            ],
                            field(default=None),
                        ),
                        ("provision_vm_agent", bool, field(default=None)),
                        ("enable_vm_agent_platform_updates", bool, field(default=None)),
                        ("disable_password_authentication", bool, field(default=None)),
                    ],
                ),
                field(default=None),
            ),
            (
                "windows_configuration",
                make_dataclass(
                    "WindowsConfiguration",
                    [
                        ("provision_vm_agent", bool, field(default=None)),
                        ("enable_vm_agent_platform_updates", bool, field(default=None)),
                        ("enable_automatic_updates", bool, field(default=None)),
                        ("time_zone", str, field(default=None)),
                    ],
                ),
                field(default=None),
            ),
        ],
    ),
    storage_os_disk: make_dataclass(
        "StorageOsDisk",
        [
            ("disk_name", str),
            ("disk_caching", str),
            ("disk_create_option", str),
            ("storage_account_type", str),
            ("disk_delete_option", str, field(default=None)),
            ("disk_size_in_GB", int, field(default=None)),
            ("disk_id", str, field(default=None)),
            ("disk_image_vhd_uri", str, field(default=None)),
            ("disk_os_type", str, field(default=None)),
            ("disk_vhd_uri", str, field(default=None)),
            ("write_accelerator_enabled", bool, field(default=None)),
        ],
    ),
    resource_id: str = None,
    subscription_id: str = None,
    resource_group_name: str = None,
    virtual_machine_name: str = None,
    virtual_machine_size: str = None,
    storage_image_reference: make_dataclass(
        "ImageReference",
        [
            ("image_sku", str, field(default=None)),
            ("image_publisher", str, field(default=None)),
            ("image_version", str, field(default=None)),
            ("image_offer", str, field(default=None)),
            ("image_id", str, field(default=None)),
            ("shared_gallery_image_id", str, field(default=None)),
            ("community_gallery_image_id", str, field(default=None)),
        ],
    ) = None,
    storage_data_disks: List[
        make_dataclass(
            "StorageDataDisks",
            [
                ("disk_create_option", str),
                ("disk_size_in_GB", int),
                ("disk_logical_unit_number", int),
                ("disk_name", str, field(default=None)),
                ("disk_caching", str, field(default=None)),
                ("disk_delete_option", str, field(default=None)),
                ("disk_id", str, field(default=None)),
                ("storage_account_type", str, field(default=None)),
            ],
        )
    ] = None,
    tags: Dict[str, str] = None,
    plan: make_dataclass(
        "Plan",
        [
            ("name", str),
            ("publisher", str),
            ("product", str),
            ("promotion_code", str, field(default=None)),
        ],
    ) = None,
    availability_set_id: str = None,
    license_type: str = None,
    boot_diagnostics: make_dataclass(
        "BootDiagnostics",
        [
            ("enabled", bool, field(default=None)),
            ("storage_uri", str, field(default=None)),
        ],
    ) = None,
    extensions_time_budget: str = None,
) -> Dict:
    r"""Create or update Virtual Machines.

    Args:
        name(str): The identifier for this state.
        location(str): Resource location. Changing this forces a new resource to be created.
        network_interface_ids(List[str]): A list of Network Interface IDs which should be associated with the Virtual Machine.
        os_profile(Dict[str, Any]): Specifies the operating system settings used while creating the virtual machine.

            * computer_name(str):
                Specifies the name of the Virtual Machine.
            * admin_username(str):
                Specifies the name of the local administrator account.
            * admin_password(str, Optional):
                (Required for Windows, Optional for Linux) The password associated with the local administrator account.
            * custom_data(str, Optional):
                Specifies a base-64 encoded string of custom data. The base-64 encoded string is decoded to a binary array that is saved as a file on the Virtual Machine. The maximum length of the binary array is 65535 bytes. Note: Do not pass any secrets or passwords in customData property. This property cannot be updated after the VM is created.
            * linux_configuration(Dict[str, Any], Optional):
                Specifies the Linux operating system settings on the virtual machine.

                * ssh_public_keys(List[Dict[str, Any]], Optional):
                    The list of SSH public keys used to authenticate with linux based VMs.

                    * key_data(str, Optional):
                        SSH public key certificate used to authenticate with the VM through ssh. The key needs to be at least 2048-bit and in ssh-rsa format.
                    * path(str, Optional):
                        Specifies the full path on the created VM where ssh public key is stored. If the file already exists, the specified key is appended to the file. Example: /home/user/.ssh/authorized_keys
                * provision_vm_agent(bool, Optional):
                    Indicates whether virtual machine agent should be provisioned on the virtual machine. When this property is not specified in the request body, default behavior is to set it to true. This will ensure that VM Agent is installed on the VM so that extensions can be added to the VM later.
                * enable_vm_agent_platform_updates(bool, Optional):
                    Indicates whether VMAgent Platform Updates is enabled for the Linux virtual machine. Default value is false.
                * disable_password_authentication(bool, Optional):
                    Specifies whether password authentication should be disabled.
            * windows_configuration(Dict[str, Any], Optional):
                Specifies Windows operating system settings on the virtual machine.

                * provision_vm_agent(bool, Optional):
                    Indicates whether virtual machine agent should be provisioned on the virtual machine. When this property is not specified in the request body, it is set to true by default. This will ensure that VM Agent is installed on the VM so that extensions can be added to the VM later.
                * enable_vm_agent_platform_updates(bool, Optional):
                    Indicates whether VMAgent Platform Updates is enabled for the Windows virtual machine. Default value is false.
                * enable_automatic_updates(bool, Optional):
                    Indicates whether Automatic Updates is enabled for the Windows virtual machine. Default value is true.
                * time_zone(str, Optional):
                    Specifies the time zone of the virtual machine. e.g. "Pacific Standard Time". Possible values can be TimeZoneInfo.Id value from time zones returned by TimeZoneInfo.GetSystemTimeZones.
        storage_os_disk(Dict[str, Any]): Specifies information about the operating system disk used by the virtual machine.

            * disk_name(str):
                Specifies the name of the OS Disk.
            * disk_caching(str, Optional):
                Specifies the caching requirements for the OS Disk. Possible values include None, ReadOnly and ReadWrite.
            * disk_create_option(str):
                Specifies how the OS Disk should be created. Possible values are Attach (managed disks only) and FromImage.
            * storage_account_type(str):
                Specifies the type of Managed Disk which should be created. Possible values are Standard_LRS, StandardSSD_LRS or Premium_LRS.
            * disk_delete_option(str, Optional):
                Specifies how the OS Disk should be handled after VM deletion. Possible values are Detach and Delete.
            * disk_size_in_GB(str, Optional):
                Specifies the size of the OS Disk in gigabytes.
            * disk_id(str, Optional):
                Specifies the ID of an existing Managed Disk which should be attached as the OS Disk of this Virtual Machine. If this is set then the create_option must be set to Attach.
            * disk_image_vhd_uri(str, Optional):
                The source user image virtual hard disk. The virtual hard disk will be copied before being attached to the virtual machine. If SourceImage is provided, the destination virtual hard drive must not exist. Specifies the virtual hard disk's uri.
            * disk_os_type(str, Optional):
                This property allows you to specify the type of the OS that is included in the disk if creating a VM from user-image or a specialized VHD. Possible values are: Windows, Linux.
            * disk_vhd_uri(str, Optional):
                Specifies the virtual hard disk's uri.
            * write_accelerator_enabled(bool, Optional):
                Specifies whether writeAccelerator should be enabled or disabled on the disk.
        resource_id(str, Optional): Virtual Machine resource id on Azure
        subscription_id(str, Optional): Subscription Unique id.
        resource_group_name(str, Optional): The name of the resource group.
        virtual_machine_name(str, Optional): The name of the virtual machine.
        virtual_machine_size(str, Optional): Specifies the size of the Virtual Machine.
        storage_image_reference(Dict[str, Any], Optional): Specifies information about the image to use. Eg- platform images, marketplace images.

            * image_sku(str, Optional):
                Specifies the SKU of the image used to create the virtual machine. Changing this forces a new resource to be created.
            * image_publisher(str, Optional):
                Specifies the publisher of the image used to create the virtual machine. Changing this forces a new resource to be created.
            * image_version(str, Optional):
                Specifies the version of the image used to create the virtual machine. Changing this forces a new resource to be created.
            * image_offer(str, Optional):
                Specifies the offer of the image used to create the virtual machine. Changing this forces a new resource to be created.
            * image_id(str, Optional):
                Resource Id
            * shared_gallery_image_id(str, Optional):
                Specified the shared gallery image unique id for vm deployment. This can be fetched from shared gallery image GET call.
            * community_gallery_image_id(str, Optional):
                Specified the community gallery image unique id for vm deployment. This can be fetched from community gallery image GET call.
        storage_data_disks(List[Dict[str, Any]], Optional): List of Data disks attached/added to a VM.

            * disk_create_option(str):
                Specifies how the data disk should be created. Possible values are Attach, FromImage and Empty.
            * disk_size_in_GB(int):
                Specifies the size of the data disk in gigabytes.
            * disk_logical_unit_number(int):
                Specifies the logical unit number of the data disk. This needs to be unique within all the Data Disks on the Virtual Machine.
            * disk_name(str, Optional):
                The name of the Data Disk.
            * disk_caching(str, Optional):
                Specifies the caching requirements for the Data Disk. Possible values include None, ReadOnly and ReadWrite.
            * disk_delete_option(str, Optional):
                Specifies how the OS Disk should be handled after VM deletion. Possible values are Detach and Delete.
            * disk_id(str, Optional):
                Specifies the ID of an Existing Managed Disk which should be attached to this Virtual Machine. When this field is set create_option must be set to Attach.
            * storage_account_type(str, Optional):
                Specifies the type of managed disk to create. Possible values are either Standard_LRS, StandardSSD_LRS, Premium_LRS or UltraSSD_LRS.
        tags(Dict[str, str], Optional): Resource tags.
        plan(Dict[str, str], Optional): Specifies information about the marketplace image used to create the virtual machine. This element is only used for marketplace images. Before you can use a marketplace image from an API, you must enable the image for programmatic use.  In the Azure portal, find the marketplace image that you want to use and then click **Want to deploy programmatically, Get Started ->**. Enter any required information and then click **Save**.

            * name(str):
                The plan ID.
            * publisher(str):
                The publisher ID.
            * product(str):
                Specifies the product of the image from the marketplace. This is the same value as Offer under the imageReference element.
            * promotion_code(str, Optional):
                The promotion code.
        availability_set_id(str, Optional): Specifies id of the availability set that the virtual machine should be assigned to. Virtual machines specified in the same availability set are allocated to different nodes to maximize availability. Currently, a VM can only be added to availability set at creation time. The availability set to which the VM is being added should be under the same resource group as the availability set resource. An existing VM cannot be added to an availability set. This property cannot exist along with a non-null properties.virtualMachineScaleSet reference.
        license_type(str, Optional): Specifies that the image or disk that is being used was licensed on-premises. Possible values for Windows Server operating system are: Windows_Client, Windows_Server. Possible values for Linux Server operating system are: RHEL_BYOS (for RHEL), SLES_BYOS (for SUSE). For more information, see Azure Hybrid Use Benefit for Windows Server and Azure Hybrid Use Benefit for Linux Server
        boot_diagnostics(Dict[str, Any], Optional): Specifies the boot diagnostic settings state. Boot Diagnostics is a debugging feature which allows you to view Console Output and Screenshot to diagnose VM status.

            * enabled(bool, Optional):
                Whether boot diagnostics should be enabled on the Virtual Machine.
            * storage_uri(str, Optional):
                Uri of the storage account to use for placing the console output and screenshot. If storageUri is not specified while enabling boot diagnostics, managed storage will be used. NOTE: If storageUri is being specified then ensure that the storage account is in the same region and subscription as the VM.
        extensions_time_budget(str, Optional): Specifies the time alloted for all extensions to start. The time duration should be between 15 minutes and 120 minutes (inclusive) and should be specified in ISO 8601 format. The default value is 90 minutes (PT1H30M).

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.compute.virtual_machines.present:
                - name: my-vm
                - resource_group_name: my-rg-1
                - virtual_machine_name: my-vm
                - location: eastus
                - virtual_machine_size: Standard_B1ls
                - network_interface_ids:
                  - /subscriptions/subscription_id/resourceGroups/my-rg-1/providers/Microsoft.Network/networkInterfaces/my-nic-id-1
                - storage_image_reference:
                    image_sku: 18.04-LTS
                    image_publisher: Canonical
                    image_version: latest
                    image_offer: UbuntuServer
                - storage_os_disk:
                    storage_account_type: Standard_LRS
                    disk_name: my-os-disk
                    disk_caching: ReadWrite
                    disk_size_in_GB: 30
                    disk_create_option: FromImage
                    disk_delete_option: Detach
                - storage_data_disks:
                  - disk_name: my-data-disk
                    disk_size_in_GB: 2
                    disk_logical_unit_number: 0
                    disk_caching: None
                    disk_create_option: Empty
                    disk_delete_option: Delete
                - os_profile:
                    admin_username: my-admin-username
                    computer_name: machine-name
                    admin_password: Vmwareadmin123!
                - tags:
                    my-tag-key-1: my-tag-value-1
                    my-tag-key-2: my-tag-value-2
    """
    result = ctx.get("wrapper_result")

    if ctx.get("skip_present"):
        return result

    if not result:
        error_message = hub.tool.azure.comment_utils.no_result_from_wrapper(
            "azure.compute.virtual_machines", name
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
        if ctx.get("test", False):
            # Return a proposed state by Idem state --test
            result["new_state"] = hub.tool.azure.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "resource_group_name": resource_group_name,
                    "subscription_id": subscription_id,
                    "virtual_machine_name": virtual_machine_name,
                    "virtual_machine_size": virtual_machine_size,
                    "tags": tags,
                    "location": location,
                    "network_interface_ids": network_interface_ids,
                    "storage_image_reference": storage_image_reference,
                    "storage_os_disk": storage_os_disk,
                    "storage_data_disks": storage_data_disks,
                    "os_profile": os_profile,
                    "resource_id": computed_resource_id,
                    "plan": plan,
                    "availability_set_id": availability_set_id,
                    "license_type": license_type,
                    "boot_diagnostics": boot_diagnostics,
                    "extensions_time_budget": extensions_time_budget,
                    "status": "running",
                },
            )
            result["comment"].append(
                f"Would create azure.compute.virtual_machines '{name}'"
            )
            return result

        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.compute.virtual_machines.convert_present_to_raw_virtual_machine(
                location=location,
                virtual_machine_size=virtual_machine_size,
                network_interface_ids=network_interface_ids,
                storage_image_reference=storage_image_reference,
                storage_os_disk=storage_os_disk,
                storage_data_disks=storage_data_disks,
                os_profile=os_profile,
                tags=tags,
                plan=plan,
                availability_set_id=availability_set_id,
                license_type=license_type,
                boot_diagnostics=boot_diagnostics,
                extensions_time_budget=extensions_time_budget,
            )

            response_put = await hub.exec.request.json.put(
                ctx,
                url=computed_resource_url,
                success_codes=[200, 201],
                json=payload,
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not create azure.compute.virtual_machines {response_put['comment']} {response_put['ret']}"
                )
                result["comment"].extend(
                    hub.tool.azure.result_utils.extract_error_comments(response_put)
                )
                result["result"] = False
                return result

            result[
                "new_state"
            ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                virtual_machine_name=virtual_machine_name,
                resource_id=computed_resource_id,
            )
            result["comment"].append(f"Created azure.compute.virtual_machines '{name}'")

            # Setting it to the initial state the VM is in after create has completed successfully
            result["new_state"]["status"] = "starting"

            return result
    else:
        raw_existing_resource = hub.tool.azure.compute.virtual_machines.convert_present_to_raw_virtual_machine(
            **existing_resource
        )
        # Generate a new PUT operation payload with new values
        new_payload = (
            hub.tool.azure.compute.virtual_machines.update_virtual_machine_payload(
                raw_existing_resource,
                existing_resource,
                {
                    "virtual_machine_size": virtual_machine_size,
                    "storage_data_disks": storage_data_disks,
                    "network_interface_ids": network_interface_ids,
                    "storage_os_disk": storage_os_disk,
                    "os_profile": os_profile,
                    "storage_image_reference": storage_image_reference,
                    "tags": tags,
                    "plan": plan,
                    "availability_set_id": availability_set_id,
                    "license_type": license_type,
                    "boot_diagnostics": boot_diagnostics,
                    "extensions_time_budget": extensions_time_budget,
                },
            )
        )

        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                hub.tool.azure.comment_utils.no_property_to_be_updated_comment(
                    "azure.compute.virtual_machines", name
                )
            )
            return result

        if ctx.get("test", False):
            result[
                "new_state"
            ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
                resource=new_payload["ret"],
                idem_resource_name=name,
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                virtual_machine_name=virtual_machine_name,
                resource_id=computed_resource_id,
            )
            # The VM status is read only and gets returned only when get is called
            # Its value will not be changed when present is called,
            # so we copy the old state to the new state at this point
            # It is only used to manage the state with the exec functions
            # It can be used from consumers to perform VM operations based on its value
            if result["old_state"].get("status"):
                result["new_state"]["status"] = result["old_state"]["status"]
            result["comment"].append(
                f"Would update azure.compute.virtual_machines '{name}'"
            )
            return result

        # PUT operation to update a resource
        response_put = await hub.exec.request.json.put(
            ctx,
            url=computed_resource_url,
            success_codes=[200, 201],
            json=new_payload["ret"],
        )
        if not response_put["result"]:
            hub.log.debug(
                f"Could not update azure.compute.virtual_machines {response_put['comment']} {response_put['ret']}"
            )
            result["result"] = False
            result["comment"].extend(
                hub.tool.azure.result_utils.extract_error_comments(response_put)
            )
            return result

        result[
            "new_state"
        ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
            resource=response_put["ret"],
            idem_resource_name=name,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            virtual_machine_name=virtual_machine_name,
            resource_id=computed_resource_id,
        )

        # The VM status is read only and gets returned only when get is called
        # Its value will not be changed when present is called,
        # so we copy the old state to the new state at this point
        # It is only used to manage the state with the exec functions
        # It can be used from consumers to perform VM operations based on its value
        if result["old_state"].get("status"):
            result["new_state"]["status"] = result["old_state"]["status"]

        result["comment"].append(f"Updated azure.compute.virtual_machines '{name}'")
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str = None,
    virtual_machine_name: str = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> Dict:
    r"""Delete a Virtual Machine.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str, Optional): The name of the resource group.
        virtual_machine_name(str, Optional): The name of the virtual machine.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): An identifier of the resource in the provider. Defaults to None.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.compute.virtual_machines.absent:
                - name: my-vm
                - resource_group_name: my-resource-group
                - virtual_machine_name: my-vm
                - subscription_id: my-subscription
    """

    # Resource deletion is handled via common recursive_contracts.init#call_absent() wrapper
    raise NotImplementedError


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Virtual Machines under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.compute.virtual_machines
    """
    result = {}
    ret_list = await hub.exec.azure.compute.virtual_machines.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe compute virtual_machines {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.compute.virtual_machines.present": [
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
