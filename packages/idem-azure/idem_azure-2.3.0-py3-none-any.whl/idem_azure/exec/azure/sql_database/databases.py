"""Exec module for managing SQL databases."""
from collections import OrderedDict
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def get(
    hub, ctx, resource_id: str, name: str = None, raw: bool = False
) -> Dict[str, Any]:
    """Get SQL Database resource by resource_id.

    Args:
        resource_id(str):
            The resource_id of database
        name(str, Optional):
            The name of the resource
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.sql_database.databases.get resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.sql_database.databases.get
                - kwargs:
                    resource_id: "/subscriptions/11111111-2222-3333-4444-555555555555/resourceGroups/default-rg/providers/Microsoft.Sql/servers/my-server/databases/my-sqldb"
      "

    """
    result = dict(comment=[], result=True, ret=None)

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-11-01",
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
            result[
                "ret"
            ] = hub.tool.azure.sql_database.databases.convert_raw_database_to_present(
                resource=response_get["ret"],
                idem_resource_name=response_get["ret"]["name"],
            )

    return result


async def list_(
    hub, ctx, resource_group_name: str = None, server_name: str = None
) -> Dict:
    """List of SQL databases

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.sql_database.databases.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.sql_database.databases.list
                - kwargs:
                  resource_group_name: default-rg
                  server_name: my-srv
    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id

    if resource_group_name is None or server_name is None:
        async for page_result in hub.tool.azure.request.paginate(
            ctx,
            url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/providers/Microsoft.Sql/servers?api-version=2021-11-01",
            success_codes=[200],
        ):
            resource_list = page_result.get("value")
            if resource_list:
                for resource in resource_list:
                    uri_parameters = OrderedDict(
                        {
                            "subscriptions": "subscription_id",
                            "resourceGroups": "resource_group_name",
                            "servers": "server_name",
                        }
                    )
                    uri_parameter_values = (
                        hub.tool.azure.uri.get_parameter_value_in_dict(
                            resource["id"], uri_parameters
                        )
                    )
                    if (
                        resource_group_name is not None
                        and resource_group_name
                        != uri_parameter_values["resource_group_name"]
                    ):
                        continue
                    if (
                        server_name is not None
                        and server_name != uri_parameter_values["server_name"]
                    ):
                        continue
                    result["ret"] += (
                        await _list_by_server(
                            hub,
                            ctx,
                            uri_parameter_values["resource_group_name"],
                            uri_parameter_values["server_name"],
                        )
                    )["ret"]
    else:
        result["ret"] += (
            await _list_by_server(hub, ctx, resource_group_name, server_name)
        )["ret"]

    return result


async def _list_by_server(hub, ctx, resource_group_name: str, server_name: str) -> Dict:
    """List of SQL databases by server

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.sql_database.databases.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.sql_database.databases.list
                - kwargs:
                  resource_group_name: default-rg
                  server_name: my-srv


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id

    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Sql/servers/{server_name}/databases?api-version=2021-11-01",
        success_codes=[200],
    ):
        resource_list = page_result.get("value")
        if resource_list:
            for resource in resource_list:
                result["ret"].append(
                    hub.tool.azure.sql_database.databases.convert_raw_database_to_present(
                        resource=resource,
                        idem_resource_name=resource["name"],
                    )
                )
        return result
