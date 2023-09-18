import copy
from typing import Dict

import dict_tools.data

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    *,
    resource_id: (str, "alias=path"),
    data: Dict,
    disable_read: bool = False,
) -> Dict:
    """
    Creates or updates a secret stored with Vault KV_v2 secret engine.

    Args:
        name (str):
            An Idem name of the resource.
        path (str):
            The full logical path to write the data. This should be prefixed 'with secret/'.
        data (str, Optional):
            Data to be written in the format of a JSON object.
        disable_read (bool, Optional):
            Set this field to True if the vault authentication does not have read access.
            However, if the value is True, this Idem state operation is not idempotent, and Idem state comment output
            will always assume it is a "create" operation. Defaults to False.

    Request Syntax:
        .. code-block:: sls

          [vault-secret-name]:
            vault.secrets.kv_v2.secret.present:
              - resource_Id: 'string' # Can also be specified as "path"
              - data: 'string'
              - disable_read: 'boolean'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            my-secret:
              vault.secrets.kv_v2.secret.present:
                - resource_id: secret/test # Can also be specified as "path"
                - data: '{"my-birthday": "2012-10-17"}'
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": (),
    }
    # data is converted to SafeNamespaceDict to avoid it being converted to string and printed to console.
    data = dict_tools.data.SafeNamespaceDict(data)
    if not disable_read:
        read_ret = await hub.exec.vault.secrets.kv_v2.secret.get(ctx, path=resource_id)
        if not read_ret["result"]:
            if "InvalidPath" not in str(read_ret["comment"]):
                result["result"] = False
                result["comment"] = read_ret["comment"]
                return result
        else:
            result["old_state"] = {
                "name": name,
                "path": resource_id,
                "data": dict_tools.data.SafeNamespaceDict(read_ret["ret"]["data"]),
            }
    else:
        hub.log.debug(f"vault.secrets.kv_v2.secret '{name}' read has been disabled.")
        result["comment"] = (
            f"vault.secrets.kv_v2.secret '{name}' read has been disabled.",
        )
    if (result["old_state"] is not None) and result["old_state"]["data"] == data:
        result["comment"] = result["comment"] + (
            f"vault.secrets.kv_v2.secret '{name}' has no property need to be updated.",
        )
        result["new_state"] = copy.deepcopy(result["old_state"])
        return result
    elif result["old_state"] is None:
        if ctx.get("test", False):
            result["comment"] = (f"Would create vault.secrets.kv_v2.secret '{name}'.",)
            result["new_state"] = {"name": name, "path": resource_id, "data": data}
            return result
    else:
        if ctx.get("test", False):
            result["comment"] = (f"Would update vault.secrets.kv_v2.secret '{name}'.",)
            result["new_state"] = {"name": name, "path": resource_id, "data": data}
            return result

    write_ret = await hub.exec.hvac.client.secrets.kv.v2.create_or_update_secret(
        ctx, path=resource_id, secret=data
    )
    if not write_ret["result"]:
        result["result"] = False
        result["comment"] = write_ret["comment"]
        return result
    result["new_state"] = {"name": name, "path": resource_id, "data": data}
    if result["old_state"] is None:
        result["comment"] = (f"Created vault.secrets.kv_v2.secret '{name}'.",)
    else:
        result["comment"] = (f"Updated vault.secrets.kv_v2.secret '{name}'.",)
    return result


async def absent(
    hub,
    ctx,
    name: str,
    *,
    resource_id: (str, "alias=path"),
    delete_all_versions: bool = False,
) -> Dict:
    """
    Deletes a secret stored with Vault KV_v2 secret engine.

    Args:
        name (str):
            An Idem name of the resource.
        resource_id (str): The full logical path to write the data.
            This argument can also be specified using the alias "path." This should be prefixed with 'secret/'.
        delete_all_versions (bool, Optional):
            Set this field to True if the vault authentication does not have read access.
            However, if the value is True, this Idem state operation is not idempotent. Defaults to False.

    Request Syntax:
        .. code-block:: sls

            [vault-secret-name]:
              vault.secrets.kv_v2.secret.absent:
                - resource_id: 'string' # Can also be specified as "path"
                - delete_all_versions: 'boolean'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            my-secret:
              vault.secrets.kv_v2.secret.absent:
                - resource_id: secret/test # Can also be specified as "path"
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": (),
    }
    read_ret = await hub.exec.vault.secrets.kv_v2.secret.get(ctx, path=resource_id)
    if not read_ret["result"]:
        if "InvalidPath" in str(read_ret["comment"]):
            result["comment"] = (
                f"vault.secrets.kv_v2.secret '{name}' is already absent.",
            )
        else:
            result["result"] = False
            result["comment"] = read_ret["comment"]
        return result

    # "data" is not populated to reduce data exposure.
    result["old_state"] = {"name": name, "path": resource_id}
    delete_version = [read_ret["metadata"]["version"]]
    if delete_all_versions:
        version_ret = await hub.exec.hvac.client.secrets.kv.v2.read_secret_metadata(
            ctx, path=resource_id
        )
        if not version_ret["result"]:
            result["result"] = False
            result["comment"] = version_ret["comment"]
            return result
        delete_version = list(version_ret["ret"]["data"]["versions"].keys())
    if ctx.get("test", False):
        if delete_all_versions:
            result["comment"] = (
                f"Would delete vault.secrets.kv_v2.secret '{name}' all versions.",
            )
        else:
            result["comment"] = (f"Would delete vault.secrets.kv_v2.secret '{name}'.",)
        return result
    delete_ret = await hub.exec.hvac.client.secrets.kv.v2.destroy_secret_versions(
        ctx, path=resource_id, versions=delete_version
    )
    if not delete_ret["result"]:
        result["result"] = False
        result["comment"] = read_ret["comment"]
    elif delete_all_versions:
        result["comment"] = (
            f"Deleted vault.secrets.kv_v2.secret '{name}' all versions.",
        )
    else:
        result["comment"] = (f"Deleted vault.secrets.kv_v2.secret '{name}'.",)
    return result


async def describe(hub, ctx):
    """
    Vault doesn't allow enumeration of secrets
    """
    return {}
