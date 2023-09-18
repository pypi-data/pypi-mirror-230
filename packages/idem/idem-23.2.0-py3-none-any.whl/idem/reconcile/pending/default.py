# Reconciliation loop stops after MAX_RERUNS_WO_CHANGE consecutive reruns with the same result/changes.
# This is to make sure we do not retry forever on failures that cannot be fixed by
# reconciliation.
MAX_RERUNS_WO_CHANGE = 3


def is_pending(hub, ret: dict, state: str = None, **pending_kwargs) -> bool:
    """
    Default implementation of pending plugin.
    Returns 'True' when the state is still 'pending' and reconciliation is required,
    otherwise 'False' to stop reconciliation.

    If the state implements is_pending() call the state's implementation,
    otherwise state is pending until 'result' is 'True' and there is no 'rerun_data'
    for normal flows, state is pending until 'result' is 'True' for resource recreation flow.
    Stop reconciliation if the last MAX_RERUNS_WO_CHANGE (3) consecutive runs produced the
    same result and 'changes', and state does NOT implement 'is_pending'.
    In any case never run more than 'max_pending_reruns' times (default 600).

    :param hub: The hub
    :param ret: (dict) Returned structure of a run
    :param state: (Text, Optional) The name of the state
    :param pending_kwargs: (dict, Optional) May include 'reruns_wo_change_count' 'reruns_count' 'max_pending_reruns'
    :return: bool
    """
    # When the state implements is_pending, we should let it determine when
    # to stop the reconciliation re-runs. However we should stop after max_reruns limit to make
    # sure we do not reconcile forever.
    max_reruns = (
        pending_kwargs.get(
            "max_pending_reruns", hub.reconcile.init.DEFAULT_MAX_PENDING_RERUNS
        )
        if pending_kwargs
        else hub.reconcile.init.DEFAULT_MAX_PENDING_RERUNS
    )

    # Flow when custom is_pending is implemented on a resource
    if (
        state is not None
        # resource with auto_state contract has no respective state sub
        and hasattr(hub.states, state)
        and hub.states[state] is not None
        and callable(getattr(hub.states[state], "is_pending", None))
    ):
        # The reconciliation should stop after MAX_RERUNS_WO_CHANGE is exhausted and result is still False.
        # This will avoid any long-running is_pending loop when there is an exception in state execution
        if (
            not ret["result"]
            and pending_kwargs
            and pending_kwargs.get("reruns_wo_change_count", 0) >= MAX_RERUNS_WO_CHANGE
        ):
            return False

        # For safety we should limit re-runs with a very large number
        # If data keeps on changing, then it runs for max_pending_reruns
        if pending_kwargs and pending_kwargs.get("reruns_count", 0) >= max_reruns:
            return False

        # Some states keep the same signature as this plugin and some receives only the 'ret'
        if "state" in hub.states[state].is_pending.signature.parameters:
            return hub.states[state].is_pending(ret=ret, state=state, **pending_kwargs)
        else:
            return hub.states[state].is_pending(ret=ret)

    # We should run more than three consecutive runs that produce the same result (errors for example).
    # Also no more than max_reruns in case the result keeps changing.
    if pending_kwargs and (
        pending_kwargs.get("reruns_wo_change_count", 0) >= MAX_RERUNS_WO_CHANGE
        or pending_kwargs.get("reruns_count", 0) >= max_reruns
    ):
        return False

    # for resource recreation flow, we should consider only whether the result is True or not.
    if ret.get("recreation_flow", False):
        return not ret["result"] is True

    # If there is re-run data or result is False, throw it back to the loop
    if not ret["result"] is True or (ret.get("rerun_data") and bool(ret["rerun_data"])):
        return True

    return False
