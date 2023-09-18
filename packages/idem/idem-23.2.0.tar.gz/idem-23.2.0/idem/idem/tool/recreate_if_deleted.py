from typing import Any
from typing import Dict
from typing import List
from typing import Tuple


async def call(hub, ctx, ret, **kwargs):
    """
    Allow Idem to re-create resource if it was deleted directly in the cloud and resource_id is managed with ESM.
    This function will clear resource_id in ESM and allow next iteration of reconciliation loop to re-create resource
    in the cloud if:
    1. present function failed and resource is not reconciling (rerun_data is empty)
    2. resource exists in ESM and resource_id is set
    3. resource has a get function in the exec module and the get for the resoruce_id returns empty result
    """

    # Do nothing if operation is successful or the resource is reconciling or resource is just updated in ESM
    if ret.get("result") or ret.get("rerun_data") or ret.get("force_save", False):
        return ret

    try:
        recreate_ret = await _recreate_resource_without_resource_id(
            hub, ctx, ret, **kwargs
        )
        return recreate_ret
    except Exception as e:
        hub.log.error(f"Failed to execute recreate_if_deleted logic: {e}")

    return ret


async def _recreate_resource_without_resource_id(hub, ctx, ret, **kwargs):
    if "run_name" not in ctx or "tag" not in ctx:
        return ret

    run_name = ctx["run_name"]
    tag = ctx["tag"]
    running = hub.idem.RUNS[run_name]["running"]
    ref = running[tag]["ref"]
    # Get the esm tag from RUNS in case the state modified it
    running_esm_tag = running[tag]["esm_tag"]
    # Get the current state
    esm_state: Dict[str, Any] = dict(hub.idem.RUNS[run_name]["managed_state"])
    if running_esm_tag in esm_state:
        esm_chunk = esm_state[running_esm_tag]
        if "resource_id" in esm_chunk:
            # Try to get resource by resource_id in the cloud and
            state_path = hub.idem.tools.tag_2_state(running_esm_tag)
            get_path = f"{state_path}.get"
            if get_path not in hub.exec:
                hub.log.debug(
                    f"Cannot clear resource_id {esm_chunk['resource_id']} in ESM for resource{ret.get('name', 'None')}. "
                    f"No 'get' operation could be found at '{ref}'"
                )
                return ret

            get_params = hub.exec[get_path].signature.parameters
            if "resource_id" not in get_params:
                hub.log.debug(
                    f"Cannot clear resource_id {esm_chunk['resource_id']} in ESM for resource{ret.get('name', 'None')}. "
                    f"Get '{ref}'.get doesn't accept resource_id."
                )
                return ret

            # Pass along any options to the "get" command that match the signature, skip hub and ctx
            get_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k in get_params
                if k != "ctx" and k != "hub"
            }
            get_args = []
            get_result = await hub.idem.ex.run(
                path=get_path,
                args=get_args,
                kwargs=get_kwargs,
                # acct info is already in the ctx
                ctx=ctx,
            )

            if not get_result.result:
                hub.log.warning(
                    f"Cannot clear resource_id {esm_chunk['resource_id']} in ESM for resource {ret.get('name', 'None')}. "
                    f"Failed to execute '{ref}'.get call with error '{get_result.comment}"
                )
                return ret

            if not get_result.get("ret", None):
                recreate_comment = (
                    f"Resource {state_path} with id {esm_chunk['resource_id']} "
                    f"is not found in the cloud provider. Re-create the resource in the cloud.",
                )

                if ctx.get("test", False):
                    # In case of the test mode, execute the function without resource id
                    kwargs.pop("resource_id", None)
                    # Call the func again
                    func = hub[ref]
                    recreate_ret = func(ctx=ctx, **kwargs)
                    recreate_ret = await hub.pop.loop.unwrap(recreate_ret)
                    comment = ["Resource present function failed."]
                    _add_comment(comment, ret["comment"])
                    _add_comment(comment, recreate_comment)
                    _add_comment(comment, recreate_ret["comment"])
                    recreate_ret["comment"] = comment
                    return recreate_ret
                else:
                    # Clear resource_id and let reconciliation retry operation without resource_id
                    comment = ["Resource present function failed."]
                    _add_comment(comment, ret["comment"])
                    _add_comment(comment, recreate_comment)
                    ret["comment"] = comment
                    esm_chunk.pop("resource_id", None)
                    return ret
    return ret


def _add_comment(comment, comment_to_add):
    if isinstance(comment_to_add, List):
        comment += comment_to_add
    elif isinstance(comment_to_add, Tuple):
        comment += list(comment_to_add)
    else:
        comment.append(comment_to_add)
