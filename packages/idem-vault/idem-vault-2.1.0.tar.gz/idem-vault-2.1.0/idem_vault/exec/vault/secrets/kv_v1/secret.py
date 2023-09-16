from typing import Dict

import dict_tools.data


async def get(hub, ctx, path: str) -> Dict:
    """
    Retrieves KV_v1 secret data-source.

    Args:
        path (str):
            The full logical path to write the data. This should be prefixed 'with secret/'.

    Request Syntax:
        [Idem-state-name]:
          exec.run:
            - path: vault.secrets.kv_v1.secret.get
            - kwargs:
                path: 'string'

    Examples:
        my-secret:
          exec.run:
            - path: vault.secrets.kv_v1.secret.get
            - kwargs:
                path: secret/test

    """
    result = dict(comment=[], ret=None, result=True)
    read_ret = await hub.exec.hvac.client.secrets.kv.v1.read_secret(ctx, path=path)
    if not read_ret["result"]:
        result["result"] = False
        result["comment"] += list(read_ret["comment"])
        return result
    result["changes"] = hub.tool.vault.secret.calculate_changes(
        new_state=read_ret["ret"]
    )
    result["ret"] = {
        "path": path,
        "data": dict_tools.data.SafeNamespaceDict(read_ret["ret"]["data"]),
    }
    return result
