from dict_tools import differ


def calculate_changes(hub, old_state=None, new_state=None):
    changes = differ.deep_diff(
        old_state["data"] if (old_state and old_state.get("data")) else dict(),
        new_state["data"] if (new_state and new_state.get("data")) else dict(),
    )
    # vault values are sensitive and should not be shown in output.
    # we will show only changed keys in the output.
    changed_keys = {}
    if changes.get("old"):
        changed_keys["old"] = {changed_key: "*" for changed_key in changes.get("old")}
    if changes.get("new"):
        changed_keys["new"] = {changed_key: "*" for changed_key in changes.get("new")}
    return changed_keys
