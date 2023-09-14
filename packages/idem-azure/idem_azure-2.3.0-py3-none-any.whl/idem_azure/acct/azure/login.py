from typing import Any
from typing import Dict

from dict_tools.data import NamespaceDict


async def gather(hub, profiles) -> Dict[str, Any]:
    """
    Get a new access token based on Azure client_id, client_secret and tenant_id

    Example:
    .. code-block:: yaml

        azure:
          profile_name:
            client_id: Azure client id "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            secret: Azure client secret "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            subscription_id: Azure subscription id "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
            tenant: Azure tenant id "cccccccc-cccc-cccc-cccc-cccccccccccc"
            api_version: 2015-07-01
    """
    sub_profiles = {}
    for (
        profile,
        ctx,
    ) in profiles.get("azure", {}).items():
        temp_ctx = NamespaceDict(acct={})
        tenant = ctx["tenant"]
        client_id = ctx["client_id"]
        secret = ctx["secret"]
        subscription_id = ctx["subscription_id"]

        login_endpoint_url = (
            ctx.get("login_endpoint_url")
            or ctx.get("endpoint_url")
            or hub.exec.azure.LOGIN_URL
        )
        resource_endpoint_url = ctx.get("endpoint_url") or hub.exec.azure.URL

        result = await hub.exec.request.json.post(
            temp_ctx,
            url=f"{login_endpoint_url}/{tenant}/oauth2/token",
            headers={
                "content-type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": secret,
                "resource": resource_endpoint_url,
            },
        )

        if not result["status"] or not result["result"]:
            status_comment = result.get("comment", "")
            error_comment = result.get("ret", "")
            error = f"Unable to authenticate with tenant '{tenant}' and client id '{client_id}': {status_comment} {error_comment}"
            hub.log.error(error)
            raise ConnectionError(error)

        ret = result.get("ret")
        if not ret or not isinstance(ret, dict):
            error = f"result['ret'] must be of type dict. Actual: ret type: {type(ret)}, ret value: {ret}"
            hub.log.error(error)
            raise TypeError(error)

        access_token = result["ret"].get("access_token")
        sub_profiles[profile] = dict(
            subscription_id=subscription_id,
            endpoint_url=resource_endpoint_url,
            login_endpoint_url=login_endpoint_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return sub_profiles
