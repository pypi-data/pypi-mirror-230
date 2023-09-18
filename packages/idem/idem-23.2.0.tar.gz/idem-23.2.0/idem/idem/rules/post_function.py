from typing import Any
from typing import Dict


def check(
    hub,
    name: str,
    ctx: Dict[str, Any],
    condition: Any,
    reqret: Dict[str, Any],
    chunk: Dict[str, Any],
    managed_state: Dict[str, Any],
    execution_seq: Dict,
) -> Dict[str, Any]:
    """
    Add a post function that will be executed after the state is executed
    """
    ret = {}
    try:
        func = getattr(hub, f'states.{chunk["state"]}.{condition}')
        if func:
            ret["post"] = func
    except AttributeError:
        try:
            func = getattr(hub, condition)
            if func:
                ret["post"] = func
        except AttributeError:
            hub.log.warning(
                f"Cannot evaluate post_low rule for state {name}. Cannot find function {condition} on the hub."
            )
    return ret
