from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from dict_tools import differ

SKIP_ESM = True


async def run(
    hub,
    ctx,
    name: str,
    *,
    path: str = None,
    acct_profile: str,
    acct_data=None,
    args: List[Any] = None,
    kwargs: Dict[str, Any] = None,
):
    """
    Call an exec module by path reference

    Args:
        hub:
        ctx:
        name(Text): The name of the state or the exec module reference path
        path(Text): The exec module reference path to call
        acct_profile(Text): The acct profile to use on the exec module call
        acct_data(Dict): The acct_data to use with the exec module call
        args(List): A list of args to pass to the exec module
        kwargs(Dict): The keyword arguments to pass to the exec module

    Returns:
        {"result": True|False, "comment": ["A message"], "new_state": The return from the exec module}


    .. code-block:: yaml

        exec_func:
          exec.run:
            - path: test.ping
            - acct_profile: default
            - args:
              - arg1
              - arg2
              - arg3
            - kwargs:
                kwarg_1: val_1
                kwarg_2: val_2
                kwarg_3: val_3
    """
    result = dict(comment=[], new_state=None, old_state=None, name=name, result=True)

    # Get defaults for each argument
    if path is None:
        path = name
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    func_ctx = await hub.idem.acct.ctx(
        path,
        profile=acct_profile,
        acct_data=acct_data or hub.idem.RUNS[ctx.run_name].get("acct_data"),
        hard_fail=True,
        validate=True,
    )

    # Other states have acct_data consumed already, but exec.run passes it forward to the exec module
    # ctx and ctx.acct have not been created yet from acct_data for the exec module.
    # At this point it is "acct_data" that needs to be removed rather than ctx or ctx.acct
    sanitized_kwargs = {k: v for k, v in kwargs.items() if k != "acct_data"}
    await hub.idem.event.put(
        profile="idem-state",
        body={name: {path: sanitized_kwargs}},
        tags={
            "ref": f"exec.{path}",
            "type": "state-pre",
            "acct_details": func_ctx.acct_details,
        },
    )

    # Report the cli command of the exec module being called
    cli_call = f"idem exec {path} --acct-profile={acct_profile}"
    if args:
        cli_call += " " + " ".join(args)
    if kwargs:
        cli_call += " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
    if "name" not in kwargs:
        try:
            resolved = hub.idem.ex.resolve(path)
            params = resolved["params"]
            if "name" in params:
                kwargs["name"] = name
        except AttributeError:
            ...

    result["comment"] += [cli_call]

    # Get the acct_data from the current run
    acct_data = acct_data or hub.idem.RUNS[ctx.run_name]["acct_data"]

    # Run the exec module!
    try:
        ret = await hub.idem.ex.run(
            path=path,
            args=args,
            kwargs=kwargs,
            acct_data=acct_data,
            acct_profile=acct_profile,
            rerun_data=ctx.get("rerun_data"),
        )
        result["result"] &= ret.result
        result["new_state"] = ret.ret
        result["rerun_data"] = ret.get("rerun_data")
        # Avoid ESM by reporting changes directly
        # Allow reading changes if changes are explicitly set in the state file.
        if ret.get("changes") is not None:
            result["changes"] = ret.get("changes")
        else:
            result["changes"] = {"new": ret.ret}

        if ret.comment:
            if isinstance(ret.comment, List):
                result["comment"] += ret.comment
            elif isinstance(ret.comment, Tuple):
                result["comment"] += list(ret.comment)
            else:
                result["comment"].append(ret.comment)
    except Exception as e:
        # Float up the errors
        result["result"] = False
        result["comment"] += [f"{e.__class__.__name__}: {e}"]

    # Fire an event using the exec module's path instead of the exec.run
    await hub.idem.event.put(
        profile="idem-state",
        body=result,
        tags={
            "ref": f"exec.{path}",
            "type": "state-post",
            "acct_details": func_ctx.acct_details,
        },
    )
    return result


async def stateful(
    hub,
    ctx,
    name: str,
    *,
    resource_id: str,
    path: str,
    esm_state_id: str = None,
    esm_state_name: str = None,
    acct_profile: str = None,
    acct_data=None,
    get_path: str = None,
    args: List[Any] = None,
    kwargs: Dict[str, Any] = None,
    get_args: List[Any] = None,
    get_kwargs: Dict[str, Any] = None,
):
    """
    Call an exec module by path reference, do a get before/after and report changes, use ESM
    By default, kwargs that are passed to the 'path' function will be forwarded to
    the 'get' function if it's signature matches the kwarg keys.
    If get_args or get_kwargs are specified, those will be used instead.
    The esm_state_id and esm_state_name together are used to create a tag that updates the
    resource state that manages this same resource via a "present" state.

    In the following example, an aws.ec2.instance.present state manages a resource.
    That same instance is rebooted in a separate state block with a separate id.
    For ESM to know that the "exec.stateful" block manages the same resource that is defined
    in the first block, we have to patch the esm_state_id and esm_state_name for the exec.stateful state
    to match the ones used in the resource.

    .. code-block:: yaml

       my_instance_state_id:
          aws.ec2.instance.present:
            name: my_state_name
            resource_id: my_id

       my_stateful_exec_id:
          exec.stateful:
              path: aws.ec2.instance.reboot
              resource_id: my_id
              esm_state_id: my_instance_state_id
              esm_state_name: my_instance_state_name


    Args:
        name(str): The name of the state or the exec module reference path
        resource_id(str): A unique identifier for the resource
        path(str): The exec module reference path to call
        esm_state_id(str, Optional): The id of the state that tracks this resource in ESM.
            If not specified, the state id from the parent is used.
        esm_state_name(str, Optional): The name of the state that tracks this resource in ESM.
            This is used to construct the ESM tag to manage the resource state.
            If not specified, it is the same as th esm_state_id.
        acct_profile(str, Optional): The acct profile to use on the exec module call
        acct_data(Dict, Optional): The acct_data to use with the exec module call
        get_path(str, Optional): The exec module reference path to a "get" call that takes resource_id
        args(List, Optional): A list of args to pass to the exec module
        kwargs(Dict, Optional): The keyword arguments to pass to the exec module
        get_args(List, Optional): A list of args to pass to the 'get' function
            If not specified, the same args are used that are passed to the "path" function
        get_kwargs(Dict, Optional): The keyword arguments to pass to the 'get' function
            If not specified, the same kwargs are used that are passed to the "path" function

    Returns:
        {"result": True|False, "comment": ["A message"], "new_state": The return from the exec module}


    .. code-block:: yaml

        exec_func:
          exec.stateful:
            - resource_id: my_resource_id
            - path: my_cloud.my_resource_group.my_resource.my_function
            - get_path: my_cloud.my_resource_group.my_resource.get
            - get_args:
              - arg1
              - arg2
              - arg3
            - get_kwargs:
                kwarg_1: val_1
                kwarg_2: val_2
                kwarg_3: val_3
            - acct_profile: default
            - esm_state_id: null
            - esm_state_name: null
            - args:
              - arg1
              - arg2
              - arg3
            - kwargs:
                kwarg_1: val_1
                kwarg_2: val_2
                kwarg_3: val_3
    """
    result = dict(comment=[], new_state=None, old_state=None, name=name, result=True)

    # Get defaults for each argument
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    exec_mod_path, func_name = path.rsplit(".", maxsplit=1)
    if func_name in ("get", "list"):
        result["result"] = False
        result["comment"].append(
            f"'{func_name}' cannot be used statefully, use exec.run for this call"
        )
        return result

    inferred_get_path = False
    # If no "get_path" was defined, make a good guess at where one will be
    if not get_path:
        inferred_get_path = True
        get_path = f"{exec_mod_path}.get"

    if get_path not in hub.exec:
        result["result"] = False
        result["comment"].append(
            f"No 'get' operation could be found at 'exec.{get_path}'"
        )
        if inferred_get_path:
            result["comment"].append(
                f"'{func_name}' cannot be used statefully, use exec.run for this call"
            )
        return result

    get_params = hub.exec[get_path].signature.parameters

    if get_args is None and get_kwargs is None:
        # Pass along any options to the "get" command that match the signature, skip ctx and hub
        get_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k in get_params
            if k != "ctx" and k != "hub"
        }
        get_args = []

        # pass forward the id of the state
        if "name" in get_params:
            get_kwargs["name"] = name

    # If only one of these was None, then they need to be cast as the correct type
    if get_args is None:
        get_args = []
    if get_kwargs is None:
        get_kwargs = {}

    if (
        hub.OPT.idem.get_resource_only_with_resource_id
        and "resource_id" not in get_params
    ):
        result["result"] = False
        result["comment"].append(
            f"Function 'exec.{get_path}' does not take 'resource_id' as a parameter!"
        )
        return result

    # Verify that we are passing a resource_id to the "get" command
    # If there is no "resource_id" parameter, then make a good guess at which parameter should receive it
    if "resource_id" in get_params:
        get_kwargs["resource_id"] = resource_id
    elif "name" in get_params:
        get_kwargs["name"] = resource_id
    elif len(get_params) > 1:
        get_args.append(resource_id)
    else:
        result["comment"].append(
            f"Function 'exec.{get_path}' does not accept 'resource_id'"
        )

    # If no esm_state_id was passed, then assume that it's under the same id as this state
    if not esm_state_id:
        _, esm_state_id, _ = ctx.tag.split("_|-", maxsplit=2)
    if not esm_state_name:
        esm_state_name = esm_state_id

    esm_state_path = exec_mod_path
    if exec_mod_path not in hub.states:
        result["comment"].append(
            f"No state for tracking resource {exec_mod_path} in ESM"
        )

    # Pass the resource id on to the main exec call
    if "resource_id" in hub.exec[path].signature.parameters:
        kwargs["resource_id"] = resource_id
    elif "name" in hub.exec[path].signature.parameters and "name" not in kwargs:
        kwargs["name"] = resource_id
    else:
        result["comment"].append(
            f"Function 'exec.{path}' does not take 'resource_id' as a parameter!"
        )

    esm_tag = hub.idem.tools.gen_chunk_esm_tag(
        dict(state=esm_state_path, __id__=esm_state_id, resource_name=esm_state_name)
    )

    # Override the esm tag in RUNS with the one for the target state
    hub.idem.RUNS[ctx.run_name]["running"][ctx.tag]["esm_tag"] = esm_tag
    # Overwrite the chunk data to use ESM for this state
    ctx.skip_esm = False

    # Get the previous state from ESM if possible
    if esm_tag in hub.idem.RUNS[ctx.run_name]["managed_state"]:
        result["old_state"] = hub.idem.RUNS[ctx.run_name]["managed_state"][esm_tag]
    else:
        pre_get = await hub.idem.ex.run(
            path=get_path,
            args=get_args,
            kwargs=get_kwargs,
            acct_data=acct_data,
            acct_profile=acct_profile,
            rerun_data=ctx.get("rerun_data"),
        )

        if not pre_get.result:
            result["comment"].append(f"Failed to perform pre-get operation")
            if isinstance(pre_get.comment, list):
                result["comment"].extend(pre_get.comment)
            else:
                result["comment"].append(pre_get.comment)
        else:
            result["old_state"] = pre_get.ret

    # Run the exec module using the exec.run state!
    ret = await hub.states.exec.run(
        ctx,
        name,
        path=path,
        acct_profile=acct_profile,
        acct_data=acct_data,
        args=args,
        kwargs=kwargs,
    )
    result["result"] = ret["result"]
    if isinstance(ret["comment"], list):
        result["comment"].extend(ret["comment"])
    elif ret["comment"]:
        result["comment"].append(ret["comment"])

    if ret["result"] is True and not ret["rerun_data"]:
        post_get = await hub.idem.ex.run(
            path=get_path,
            args=get_args,
            kwargs=get_kwargs,
            acct_data=acct_data,
            acct_profile=acct_profile,
            rerun_data=ctx.get("rerun_data"),
        )
        if not post_get.result:
            result["comment"].append(f"Failed to perform post-get operation")
            if isinstance(post_get.comment, list):
                result["comment"].extend(post_get.comment)
            else:
                result["comment"].append(post_get.comment)

        result["new_state"] = post_get.ret
        result["changes"] = differ.deep_diff(
            result["old_state"],
            result["new_state"],
        )
    return result


def is_pending(hub, ret: dict, state: str = None, **pending_kwargs) -> bool:
    """
    Pending implementation of exec.run
    Pending if the 'result' is False. The state will reconcile as long as there is rerun_data.
    Otherwise, reconciliation will stop after MAX_RERUNS_WO_CHANGE number of attempts.

    :return: True if reconciliation is required. If result is True do not reconcile.
    """
    if not ret["result"]:
        if ret.get("rerun_data"):
            # Continue reconciling for as long as there is rerun_data
            return True
        elif (
            pending_kwargs
            and pending_kwargs.get("reruns_wo_change_count", 0)
            >= hub.reconcile.pending.default.MAX_RERUNS_WO_CHANGE
        ):
            # Otherwise stop after MAX_RERUNS_WO_CHANGE times
            return False
        else:
            return True
    else:
        return False
