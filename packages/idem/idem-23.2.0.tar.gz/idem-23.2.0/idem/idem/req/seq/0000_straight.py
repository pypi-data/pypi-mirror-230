from typing import Any
from typing import Dict


def run(
    hub,
    seq: Dict[int, Dict[str, Any]],
    low: Dict[str, Any],
    running: Dict[str, Any],
    options: Dict[str, Any],
) -> Dict[int, Dict[str, Any]]:
    """
    Return the sequence map that should be used to execute the lowstate
    The sequence needs to identify:
    1. recursive requisites
    2. what chunks are free to run
    3. Behavior augments for the next chunk to run
    """
    ret = {}
    for ind, chunk in enumerate(low):
        tag = hub.idem.tools.gen_chunk_func_tag(chunk)
        if tag in running:
            # Already ran this one, don't add it to the sequence
            continue
        ret[ind] = {
            "chunk": chunk,
            "reqrets": [],
            "unmet": set(),
            "tag": tag,
            "errors": [],
        }
        for req, data in hub.idem.RMAP.items():
            if (
                data.get("prereq")
                or data.get("sensitive")
                or data.get("recreate_on_update")
            ):
                continue
            if req in chunk:
                for rdef in chunk[req]:
                    if not isinstance(rdef, dict):
                        continue
                    state = next(iter(rdef))
                    if isinstance(rdef[state], list):
                        name_defs = rdef[state]
                    else:
                        name_defs = [{rdef[state]: []}]

                    for name_def in name_defs:
                        if not isinstance(name_def, dict):
                            ret[ind]["errors"].append(
                                f"{name_def} should be dictionary"
                            )
                            continue
                        state_name = next(iter(name_def))
                        # Format  might be 'state' or 'state[resource_name]', where state is the declaration id
                        (
                            name,
                            resource_name,
                        ) = hub.tool.idem.arg_bind_utils.parse_state_id(state_name)
                        args = name_def[state_name]
                        r_chunks = hub.idem.tools.get_chunks(
                            low, state, name, resource_name
                        )
                        if not r_chunks:
                            if not state.split(".")[0] in hub.states:
                                msg = f"Requisite '{req}' state '{state}': not found in current run. Verify the syntax."
                                hub.log.error(f"msg")
                                ret[ind]["errors"].append(msg)
                            elif getattr(
                                hub.states[state.split(".")[0]], "SKIP_ESM", False
                            ):
                                # If state has SKIP_ESM flag we should fail. The format might be wrong.
                                msg = f"Requisite '{req} {state}:{name}' not found in current run. Verify the syntax."
                                hub.log.error(f"msg")
                                ret[ind]["errors"].append(msg)
                            else:
                                # For arg_bind and 'require' there is an additional step to check in ESM.
                                # Error will be added there if we do not find requisite in ESM.
                                hub.log.debug(
                                    f"Requisite '{req} {state}:{name}' not found in current run. For 'arg_bind' and "
                                    f"'require' requisites, there is an additional step to check in ESM."
                                )
                            if req not in ["arg_bind", "require"]:
                                ret[ind]["errors"].append(
                                    f"Invalid requisite '{req} {state}:{name}'. Expected 'arg_bind' or 'require'."
                                )
                        # We might have references to the same state but with different state_name (some from ESM)
                        for r_chunk in r_chunks:
                            r_tag = hub.idem.tools.gen_chunk_func_tag(r_chunk)
                            if r_tag in running:
                                reqret = {
                                    "req": req,
                                    "name": state_name,
                                    "state": state,
                                    "r_tag": r_tag,
                                    "ret": running[r_tag],
                                    "chunk": "r_chunk",
                                    "args": args,
                                }
                                # it has been run, check the rules
                                ret[ind]["reqrets"].append(reqret)
                            else:
                                ret[ind]["unmet"].add(r_tag)
    return ret
