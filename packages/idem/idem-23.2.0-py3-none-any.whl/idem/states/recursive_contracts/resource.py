import asyncio
import warnings
from typing import Any
from typing import Dict
from typing import List


TREQ = {
    # Set recreate_if_deleted to empty list to make sure that
    # it will merge with other requisites defined on the resource.
    "present": {"recreate_if_deleted": []},
}


def sig_present(hub, ctx, name: str, *args, **kwargs):
    ...


def sig_absent(hub, ctx, name: str, *args, **kwargs):
    ...


async def sig_describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    ...


def post_present(hub, ctx):
    ret = _create_state_return(hub, ctx)
    return ret


def post_absent(hub, ctx):
    return _create_state_return(hub, ctx)


def _create_state_return(hub, ctx):
    """
    Conform the output of every state return to this format.
    Valid state modules must return a dictionary with these keys
    Validate the output of every state return format.

    The recalculation of the state "changes" happens only when there is old_state, new_state
    and changes are "None" (not empty dict). This way we avoid infinite
    reconciliation, which happened due to the value of reruns_wo_change_count
    not being changed (track value in "idem/reconcile/basic.py").
    Enhanced the "else" that is used for giving the warning for required old and new state
    by making it an elif which has a check if there is no old_state or no new_state.
    """
    if not ctx.ret:
        raise ValueError(f"No return from state")
    if (
        "old_state" in ctx.ret
        and "new_state" in ctx.ret
        # Allow resource state to explicitly set changes to empty collection
        # to allow for the case when changes must be ignored during reconciliation process
        and ctx.ret.get("changes") is None
    ):
        params = ctx.signature.parameters
        old_state = ctx.ret.get("old_state")
        new_state = ctx.ret.get("new_state")
        ctx.ret["changes"] = hub.tool.idem.arg_utils.calculate_changes(
            old_state, new_state, params, ctx.ref
        )
    elif "changes" not in ctx.ret:
        hub.log.error(
            "States that implement 'resource' contract must either return 'changes' "
            "or a combination of 'old_state' and 'new_state'."
        )
    elif "old_state" not in ctx.ret or "new_state" not in ctx.ret:
        # TODO Raise an error here instead of a warning
        warnings.warn(
            f"It is required to return both 'old_state' and 'new_state' for the 'resource' contract.",
            DeprecationWarning,
        )
    # Prevent any sensitive data showing in "changes", which will be outputted to console.
    if "changes" in ctx.ret:
        arguments = ctx.get_arguments()
        if "run_name" in arguments["ctx"] and "tag" in arguments["ctx"]:
            run_name = arguments["ctx"]["run_name"]
            tag = arguments["ctx"]["tag"]
            if (
                "sensitive" in hub.idem.RUNS[run_name]
                and tag in hub.idem.RUNS[run_name]["sensitive"]
            ):
                # Put data-sanitization here because this is the closest to the Idem state module return.
                # However, in general, we should avoid adding too much functionalities in the contract's "post" signature.
                # Instead, the recommendation is to have a "post-rule" plugin to run after Idem state runs.
                if ctx.ret["changes"] and ctx.ret["changes"].get("new"):
                    for sensitive_data in hub.idem.RUNS[run_name]["sensitive"][tag]:
                        ctx.ret["changes"]["new"].pop(sensitive_data, None)
                if ctx.ret["changes"] and ctx.ret["changes"].get("old"):
                    for sensitive_data in hub.idem.RUNS[run_name]["sensitive"][tag]:
                        ctx.ret["changes"]["old"].pop(sensitive_data, None)

    try:
        return {
            "changes": ctx.ret["changes"],
            "comment": ctx.ret["comment"],
            "name": ctx.ret["name"],
            "result": ctx.ret["result"],
            "old_state": ctx.ret.get("old_state", None),
            "new_state": ctx.ret.get("new_state", None),
            "force_save": ctx.ret.get("force_save", False),
            "rerun_data": ctx.ret.get("rerun_data", None),
        }
    except KeyError:
        hub.log.error(f"Improperly formatted state return: {ctx.ref}")
        raise


def _verify_describe(hub, ret: Dict[str, Dict[str, Any]]):
    """
    Verify that the return value looks like
    {
        state_name: { path.present: [{},...] }
    }
    """
    for present_state in ret.values():
        for state_path, state_data in present_state.items():
            assert isinstance(
                state_data, List
            ), "State information should be formatted as a list"
            for item in state_data:
                assert isinstance(item, Dict), "Each item in the list should be a dict"
    return ret


async def _averify_describe(hub, ret):
    """
    Return a coroutine to a function that is expecting a coroutine
    """
    return _verify_describe(hub, await ret)


def pre_describe(hub, ctx):
    if hasattr(hub, "SUBPARSER"):
        if hub.SUBPARSER not in ("describe", "refresh"):
            raise ReferenceError(
                "'describe' functions should only be called by the describe subcommand."
                f"Please refer to the {ctx.ref} plugin documentation for 'search' functionality."
            )


def post_describe(hub, ctx):
    if asyncio.iscoroutine(ctx.ret):
        return _averify_describe(hub, ctx.ret)
    else:
        return _verify_describe(hub, ctx.ret)
