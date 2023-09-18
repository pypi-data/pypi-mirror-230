import asyncio
import copy
import datetime
from typing import Any
from typing import Dict
from typing import List


# Sleep time in seconds between re-runs
DEFAULT_RECONCILE_WAIT = 3
# Dictionary for the default static sleep time
DEFAULT_STATIC_RECONCILE_WAIT = {"static": {"wait_in_seconds": DEFAULT_RECONCILE_WAIT}}
# Dictionary keeping state's reconcile wait time in seconds
_state_to_sleep_map = {}


async def loop(
    hub,
    pending_plugin: str,
    max_pending_reruns: int,
    name: str,
    apply_kwargs: Dict[str, Any],
):
    """
    This loop attempts to apply states.
    This function returns once all the states are successful or after MAX_RERUNS_WO_CHANGE has been reached, whatever
    occurs first.
    The sleep time between each attempt will be determined by a "wait" plugin and might change between each iterations.
    Reconciliation is required if the state is "pending" as defined by the pending plugin.
    The default pending plugin defines pending state if result  is not 'True' or there are 'changes'.

    @param hub:
    @param pending_plugin: plugin name for checking if the state is pending based on the result
    @param name: name of the run
    @param apply_kwargs: possible addition arguments
    @param max_pending_reruns: the maximum number of reruns before returning False to stop reconciliation of the resource
    :return: dictionary { "re_runs_count": <number of re-runs that occurred> }
    """
    # Record the first run as following reconciliation re-runs will
    # include subset of pending states
    first_run = copy.deepcopy(hub.idem.RUNS[name]["running"])
    tag_to_reruns_wo_change_count = {}

    # Populate wait time algorithm and values for the different states
    # in this run. State has to define __reconciliation_wait__
    # with values such as:
    # { "exponential": {"wait_in_seconds": 2, "multiplier": 10} }
    # { "static": {"wait_in_seconds": 3} }
    # { "random": {"min_value": 1, "max_value": 10} }
    hub.reconcile.basic.populate_wait_times(first_run)

    # Concatenate comments for pending tags
    tag_to_comments = hub.reconcile.basic.populate_comments(first_run)
    current_run = hub.idem.RUNS[name]["running"]

    count = 0
    while True:
        pending_tags = hub.reconcile.basic.get_pending_tags(
            pending_plugin=pending_plugin,
            runs=current_run,
            tag_to_reruns_wo_change_count=tag_to_reruns_wo_change_count,
            reruns_count=count,
            max_pending_reruns=max_pending_reruns,
            ctx=apply_kwargs.get("ctx"),
        )

        if not pending_tags:
            hub.log.debug(f"Finished reconciliation loop, updating state results.")
            await hub.reconcile.basic.update_result_and_send_event(
                first_run,
                current_run,
                tag_to_comments,
            )
            hub.idem.RUNS[name]["running"] = first_run
            hub.log.debug(f"Reconciliation loop returns after {count} runs.")
            return {"re_runs_count": count}

        # Update result for states that finished reconciling
        if count > 0 and len(pending_tags) < len(current_run):
            already_reconciled_tags = [
                tag for tag in current_run if tag not in pending_tags
            ]
            if already_reconciled_tags:
                already_reconciled_run = {}
                for tag in already_reconciled_tags:
                    already_reconciled_run[tag] = copy.deepcopy(current_run.get(tag))
                await hub.reconcile.basic.update_result_and_send_event(
                    first_run,
                    already_reconciled_run,
                    tag_to_comments,
                )

        sleep_time_sec = get_max_wait_time(hub, count, pending_tags)
        hub.log.debug(
            f"Sleeping {sleep_time_sec} seconds for {name} before reconciling [{pending_tags}]"
        )
        await asyncio.sleep(sleep_time_sec)

        count = count + 1
        hub.log.debug(f"Reconciliation retry {count} for {name}")

        last_run = current_run

        # Re-run pending states
        await hub.idem.run.init.start(name, pending_tags)

        # This run will include only the pending tags
        current_run = hub.idem.RUNS[name]["running"]
        hub.reconcile.basic.populate_comments(current_run, tag_to_comments)
        hub.reconcile.basic.populate_no_changes_count(
            last_run, current_run, tag_to_reruns_wo_change_count
        )


def get_pending_tags(
    hub,
    pending_plugin: str,
    runs: Dict,
    tag_to_reruns_wo_change_count: Dict,
    reruns_count: int,
    max_pending_reruns: int,
    ctx: Dict = None,
):
    # invoke pending plugin and populate pending tags
    pending_tags = []
    for tag in runs:
        if (
            "pending_kwargs"
            in hub.reconcile.pending[pending_plugin].is_pending.signature.parameters
        ):
            pending_kwargs = {
                "ctx": ctx,
                "reruns_wo_change_count": tag_to_reruns_wo_change_count.get(tag, 0),
                "reruns_count": reruns_count,
                "max_pending_reruns": max_pending_reruns,
            }
            if hub.reconcile.pending[pending_plugin].is_pending(
                ret=runs[tag],
                state=hub.idem.tools.tag_2_state(tag),
                **pending_kwargs,
            ):
                pending_tags.append(tag)
        elif hub.reconcile.pending[pending_plugin].is_pending(
            ret=runs[tag],
            state=hub.idem.tools.tag_2_state(tag),
        ):
            pending_tags.append(tag)

    return pending_tags


def populate_wait_times(hub, runs):
    # Populate sleep times per state
    for tag in runs:
        state = hub.idem.tools.tag_2_state(tag)

        if not hasattr(hub.states, state):
            # resource with auto_state contract has no respective state sub
            _state_to_sleep_map[state] = DEFAULT_STATIC_RECONCILE_WAIT

        if state not in _state_to_sleep_map.keys():
            try:
                _state_to_sleep_map[state] = getattr(
                    hub.states[state],
                    "__reconcile_wait__",
                    DEFAULT_STATIC_RECONCILE_WAIT,
                )
            except Exception as e:
                hub.log.error(
                    f"Failed to retrieve sleep time for state {state}: {e.__class__.__name__}: {e}"
                )
                _state_to_sleep_map[state] = DEFAULT_STATIC_RECONCILE_WAIT


def get_max_wait_time(hub, run_count, pending_tags: List[str]):
    # Return the maximum wait time among the pending tags
    max_sleep_time = DEFAULT_RECONCILE_WAIT
    for tag in pending_tags:
        state_wait = _state_to_sleep_map.get(
            hub.idem.tools.tag_2_state(tag), DEFAULT_STATIC_RECONCILE_WAIT
        )
        wait_alg = list(state_wait.keys())[0]
        wait_val = state_wait[wait_alg]
        sleep_time = hub.reconcile.wait[wait_alg].get(**wait_val, run_count=run_count)
        if sleep_time > max_sleep_time:
            max_sleep_time = sleep_time

    return max_sleep_time


async def update_result_and_send_event(
    hub,
    first_run,
    last_run,
    tag_to_comments: Dict[str, tuple],
):
    # Merge last_run results of tags that finished reconciling,
    # into first_run, recalculate changes to reflect
    # all the changes that occurred during reconciliation:
    # the delta between original run's 'old_state' and last_run 'new_state'
    # Update 'comment' with the cumulative comments from all runs (w/o duplicates)
    # and send a 'state-result' event
    if not last_run:
        return

    for tag in last_run:
        if tag in first_run:
            last_run[tag].pop("start_time", None)
            last_run[tag].pop("old_state", None)
            first_run[tag].update(last_run[tag])
            # Calculate new changes
            if not first_run[tag].get("old_state", {}) and not first_run[tag].get(
                "new_state", {}
            ):
                hub.log.debug(
                    f"Skip calculating 'changes' for {first_run[tag].get('name')}, since 'old_state' and "
                    f"'new_state' are not set."
                )
            if not isinstance(first_run[tag].get("old_state"), dict) or not isinstance(
                first_run[tag].get("new_state"), dict
            ):
                hub.log.debug(
                    f"Skip calculating 'changes' for {first_run[tag].get('name')}, since 'old_state' and/or "
                    f"'new_state' are not dictionaries."
                )
            # Configure changes only if there is new_state and old_state, otherwise the state didn't execute
            else:
                first_run[tag]["changes"] = hub.tool.idem.arg_utils.calculate_changes(
                    first_run[tag].get("old_state") or {},
                    first_run[tag].get("new_state") or {},
                    getattr(hub, last_run[tag].get("ref")).signature.parameters,
                    last_run[tag].get("ref"),
                )
            if tag_to_comments.get(tag):
                first_run[tag]["comment"] = tag_to_comments.get(tag)
        else:
            hub.log.debug(f"Adding a tag to the run during reconciliation {tag}")
            first_run[tag] = last_run[tag]

        # Send 'state-result' event with the updated information
        await send_state_result_event(hub, first_run[tag])


async def send_state_result_event(hub, tag_ret):
    # Last 'state-result' for the resource
    # Includes complete delta of 'changes' and total time (include multiple elapsed reconciliation)
    if tag_ret.get("start_time"):
        tag_ret["total_seconds"] = (
            datetime.datetime.now()
            - datetime.datetime.fromisoformat(tag_ret.get("start_time"))
        ).total_seconds()
    tags = {
        "ref": tag_ret.get("ref"),
        "type": "state-result",
        "acct_details": tag_ret.get("acct_details"),
    }
    tag_ret.pop("ref", None)
    tag_ret.pop("acct_details", None)
    await hub.idem.event.put(
        profile="idem-run",
        body=tag_ret,
        tags=tags,
    )


def populate_comments(
    hub, run, tag_to_comments: Dict[str, tuple] = None
) -> Dict[str, tuple]:
    # If tag_to_comments is empty populate it with the run comments.
    # Otherwise add comments to existing
    if not tag_to_comments:
        tag_to_comments = {}
    for tag in run:
        # We expect comments to be of type tuple
        if run[tag].get("comment"):
            comment = run[tag].get("comment")
            if isinstance(comment, str):
                hub.log.debug(
                    f"Expecting a comment of type tuple but got a str: {comment}"
                )
                comment = (comment,)
            elif isinstance(comment, list):
                hub.log.debug(
                    f"Expecting a comment of type tuple but got a list: {comment}"
                )
                comment = tuple(comment)
            elif not isinstance(comment, tuple):
                hub.log.warning(
                    f"Unsupported comment type: {type(comment)}, comment: {str(comment)}"
                )
                continue

            if tag_to_comments.get(tag) and not comment[0] in tag_to_comments.get(tag):
                tag_to_comments[tag] += comment
            else:
                tag_to_comments[tag] = comment

    return tag_to_comments


def populate_no_changes_count(
    hub, last_run, current_run, tag_to_reruns_wo_change_count: Dict[str, int] = None
):
    # If tag_to_comments is empty populate it with the run comments.
    # Otherwise add comments to existing
    if not last_run or not current_run:
        return
    for tag in current_run:
        if last_run.get(tag):
            if (
                last_run[tag]["result"] == current_run[tag]["result"]
                and last_run[tag]["changes"] == current_run[tag]["changes"]
            ):
                tag_to_reruns_wo_change_count[tag] = (
                    tag_to_reruns_wo_change_count.get(tag) + 1
                    if tag_to_reruns_wo_change_count.get(tag)
                    else 1
                )
            else:
                tag_to_reruns_wo_change_count[tag] = 0


def _populate_old_states(run):
    # Keep old_state per tag from the original run
    tag_to_old_state = {}
    for tag in run:
        if run[tag].get("old_state", None):
            tag_to_old_state[tag] = copy.deepcopy(run[tag]["old_state"])
    return tag_to_old_state
