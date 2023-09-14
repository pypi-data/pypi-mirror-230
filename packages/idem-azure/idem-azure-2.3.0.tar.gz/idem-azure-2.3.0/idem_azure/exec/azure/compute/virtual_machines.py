"""Exec module for managing Compute Virtual Machines."""
from collections import OrderedDict
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


RESOURCE_TYPE = "compute.virtual_machines"


async def get(
    hub, ctx, resource_id: str, name: str = None, raw: bool = False
) -> Dict[str, Any]:
    """Get compute virtual machines resource from resource_id.

    Args:
        resource_id(str):
            The resource_id of virtual machine
        name(str, Optional):
            The name of the resource
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.get resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.compute.virtual_machines.get
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"

    """
    result = dict(comment=[], result=True, ret=None)
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "virtualMachines": "virtual_machine_name",
        }
    )
    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version={api_version}&$expand=instanceView",
        success_codes=[200],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"].extend(
            hub.tool.azure.result_utils.extract_error_comments(response_get)
        )
        return result

    elif response_get["result"] and response_get["ret"]:
        if raw:
            result["ret"] = response_get["ret"]
        else:
            uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                resource_id, uri_parameters
            )
            result[
                "ret"
            ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
                resource=response_get["ret"],
                idem_resource_name=resource_id,
                resource_id=resource_id,
                **uri_parameter_values,
            )

    return result


async def list_(hub, ctx) -> Dict:
    """List of compute virtual machines

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.compute.virtual_machines.list


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "resourceGroups": "resource_group_name",
            "virtualMachines": "virtual_machine_name",
        }
    )
    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Compute/virtualMachines?api-version={api_version}",
        success_codes=[200],
    ):
        resource_list = page_result.get("value")
        if resource_list:
            for resource in resource_list:
                resource_id = resource["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )
                result["ret"].append(
                    hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        subscription_id=subscription_id,
                        resource_id=resource_id,
                        **uri_parameter_values,
                    )
                )
    return result


async def power_off(
    hub, ctx, resource_id: str, skip_shutdown: bool = False
) -> Dict[str, Any]:
    """The operation to power off (stop) a virtual machine. The virtual machine can be restarted with the same provisioned resources. You are still charged for this virtual machine.

    Args:
        resource_id(str):
            The resource_id of virtual machine
        skip_shutdown(bool, Optional):
            The parameter to request non-graceful VM shutdown. True value for this flag indicates non-graceful shutdown whereas false indicates otherwise. Default value for this flag is false if not specified

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.power_off resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.compute.virtual_machines.power_off
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"

    """

    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    result = await hub.tool.azure.generic.exec_request(
        ctx,
        resource_id=resource_id,
        request_method="post",
        api_method="powerOff",
        query_params={"skipShutdown": skip_shutdown},
        api_version=api_version,
        resource_idem_path=f"azure.{RESOURCE_TYPE}",
    )

    return result


async def start(hub, ctx, resource_id: str) -> Dict[str, Any]:
    """The operation to start a virtual machine.

    Args:
        resource_id(str):
            The resource_id of virtual machine

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.start resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.compute.virtual_machines.start
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"

    """

    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    result = await hub.tool.azure.generic.exec_request(
        ctx,
        resource_id=resource_id,
        request_method="post",
        api_method="start",
        api_version=api_version,
        resource_idem_path=f"azure.{RESOURCE_TYPE}",
    )

    return result


async def restart(hub, ctx, resource_id: str) -> Dict[str, Any]:
    """The operation to restart a virtual machine.

    Args:
        resource_id(str):
            The resource_id of virtual machine

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.restart resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.compute.virtual_machines.restart
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"

    """

    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    result = await hub.tool.azure.generic.exec_request(
        ctx,
        resource_id=resource_id,
        request_method="post",
        api_method="restart",
        api_version=api_version,
        resource_idem_path=f"azure.{RESOURCE_TYPE}",
    )

    return result


async def deallocate(
    hub, ctx, resource_id: str, hibernate: bool = None
) -> Dict[str, Any]:
    """Shuts down the virtual machine and releases the compute resources. You are not billed for the compute resources that this virtual machine uses.

    Args:
        resource_id(str):
            The resource_id of virtual machine
        hibernate(bool, Optional):
            Optional parameter to hibernate a virtual machine. (Feature in Preview)

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.deallocate resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.compute.virtual_machines.deallocate
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"

    """

    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    result = await hub.tool.azure.generic.exec_request(
        ctx,
        resource_id=resource_id,
        request_method="post",
        api_method="deallocate",
        query_params={"hibernate": hibernate},
        api_version=api_version,
        resource_idem_path=f"azure.{RESOURCE_TYPE}",
    )

    return result


async def perform_maintenance(hub, ctx, resource_id: str) -> Dict[str, Any]:
    """The operation to perform maintenance on a virtual machine.

    Args:
        resource_id(str):
            The resource_id of virtual machine

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.perform_maintenance resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.compute.virtual_machines.perform_maintenance
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"

    """

    api_version = hub.tool.azure.api_versions.get_api_version(RESOURCE_TYPE)
    result = await hub.tool.azure.generic.exec_request(
        ctx,
        resource_id=resource_id,
        request_method="post",
        api_method="performMaintenance",
        api_version=api_version,
        resource_idem_path=f"azure.{RESOURCE_TYPE}",
    )

    return result
