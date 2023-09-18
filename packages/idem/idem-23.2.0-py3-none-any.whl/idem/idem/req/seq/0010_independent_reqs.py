from typing import Any
from typing import Dict

INDEPENDENT_REQUISITES = ["sensitive", "recreate_on_update", "recreate_if_deleted"]


def run(
    hub,
    seq: Dict[int, Dict[str, Any]],
    low: Dict[str, Any],
    running: Dict[str, Any],
    options: Dict[str, Any],
) -> Dict[int, Dict[str, Any]]:
    """
    Process the requisites that do not depend on other states.
    """
    for ind, data in seq.items():
        for req in INDEPENDENT_REQUISITES:
            if req not in data["chunk"]:
                continue
            chunk = data["chunk"]
            r_tag = hub.idem.tools.gen_chunk_func_tag(chunk)
            reqret = {
                "r_tag": r_tag,
                "req": req,
                "ret": {},
            }
            data["reqrets"].append(reqret)

    return seq
