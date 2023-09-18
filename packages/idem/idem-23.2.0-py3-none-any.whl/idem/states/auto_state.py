# States for exec modules that implement the "auto_state" contract
import uuid

import dict_tools.differ as differ

__contracts__ = ["resource"]


async def present(
    hub, ctx, name: str, resource_id: str = None, exec_mod_ref=None, **kwargs
):
    """
    Create a resource if it doesn't exist, update otherwise
    """
    result = dict(
        comment=[], old_state={}, new_state={}, name=name, result=True, rerun_data=None
    )

    desired_state = {"name": name, "resource_id": resource_id, **kwargs}

    if resource_id:
        before = await hub.pop.loop.unwrap(
            hub.exec[exec_mod_ref].get(ctx, name, resource_id, **kwargs)
        )
        result["old_state"] = before.ret

        if not before["result"] or not before["ret"]:
            result["result"] = False
            result["comment"] = before["comment"]
            return result

        result["comment"].append(f"'{exec_mod_ref}:{name}' already exists")

        # If there are changes in desired state from existing state
        changes = differ.deep_diff(before.ret if before.ret else {}, desired_state)

        if bool(changes.get("new")):
            if ctx.test:
                result["new_state"] = desired_state
                result["comment"].append(f"Would update {exec_mod_ref}:{name}")
                return result
            else:
                # Update the resource
                update_ret = await hub.pop.loop.unwrap(
                    hub.exec[exec_mod_ref].update(ctx, name, resource_id, **kwargs)
                )
                result["result"] = update_ret["result"]

                if result["result"]:
                    result["comment"].append(f"Updated '{exec_mod_ref}:{name}'")
                else:
                    result["comment"].append(update_ret["comment"])
    else:
        if ctx.test:
            result["new_state"] = desired_state
            result["comment"].append(f"Would create {exec_mod_ref}:{name}")
            return result
        else:
            create_ret = await hub.pop.loop.unwrap(
                hub.exec[exec_mod_ref].create(ctx, name, **kwargs)
            )
            result["result"] = create_ret["result"]

            if result["result"]:
                result["comment"].append(f"Created '{exec_mod_ref}:{name}'")
                resource_id = create_ret["ret"]["resource_id"]
                # Safeguard for any future errors so that the resource_id is saved in the ESM
                result["new_state"] = dict(name=name, resource_id=resource_id)
            else:
                result["comment"].append(create_ret["comment"])

    if not result["result"]:
        # If there is any failure in create/update, it should reconcile.
        # The type of data is less important here to use default reconciliation
        # If there are no changes for 3 runs with rerun_data, then it will come out of execution
        result["rerun_data"] = dict(name=name, resource_id=resource_id)

    after = await hub.pop.loop.unwrap(
        hub.exec[exec_mod_ref].get(ctx, name, resource_id, **kwargs)
    )
    result["new_state"] = after.ret
    return result


async def absent(
    hub, ctx, name: str, resource_id: str = None, exec_mod_ref=None, **kwargs
):
    """
    Remove a resource if it exists
    """
    result = dict(
        comment=[], old_state={}, new_state={}, name=name, result=True, rerun_data=None
    )

    if not resource_id:
        resource_id = (ctx.old_state or {}).get("resource_id")

    if not resource_id:
        result["comment"].append(f"'{exec_mod_ref}:{name}' already absent")
        return result

    # Remove resource_id from kwargs to avoid duplicate argument
    before = await hub.pop.loop.unwrap(
        hub.exec[exec_mod_ref].get(ctx, name, resource_id, **kwargs)
    )

    if before["ret"]:
        if ctx.test:
            result["comment"] = f"Would delete {exec_mod_ref}:{name}"
            return result

        delete_ret = await hub.pop.loop.unwrap(
            hub.exec[exec_mod_ref].delete(ctx, name, resource_id, **kwargs)
        )
        result["result"] = delete_ret["result"]

        if result["result"]:
            result["comment"].append(f"Deleted '{exec_mod_ref}:{name}'")
        else:
            # If there is any failure in create/update, it should reconcile.
            # The type of data is less important here to use default reconciliation
            # If there are no changes for 3 runs with rerun_data, then it will come out of execution
            result["rerun_data"] = resource_id
            result["comment"].append(delete_ret["result"])
    else:
        result["comment"].append(f"'{exec_mod_ref}:{name}' already absent")
        return result

    result["old_state"] = before.ret
    return result


async def describe(hub, ctx):
    """
    Create "present" states for a resource based on an "auto_state" exec module plugin
    """
    exec_mod_ref = ctx.exec_mod_ref
    result = {}

    ret = await hub.pop.loop.unwrap(hub.exec[exec_mod_ref].list(ctx))

    if not (ret["result"] and ret["ret"]):
        return result

    for resource in ret["ret"]:
        resource_id = (
            resource.get("resource_id") or f"{resource.get('name')}-{uuid.uuid4()}"
        )
        # assumption is that all conversion has taken place in list method
        present_state = [{k: v} for k, v in resource.items()]
        result[resource_id] = {f"{exec_mod_ref}.present": present_state}

    return result
