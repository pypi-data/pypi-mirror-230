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
    Invert the requisites. If invert command line parameter is specified, requisites
    need to be reverted as well since order of execution is exact reverse in case of
    present and absent function references. The following code achieves the same.
    """
    if "invert_state" not in options or not options["invert_state"]:
        hub.log.debug("Skipping invert as not enabled")
        return seq

    tag_state_map = {}
    for ind, data in seq.items():
        tag_state_map[data["tag"]] = ind

    unmets = {}
    for data in seq.values():
        if "unmet" not in data:
            continue
        if (
            "fun" in data["chunk"]
            and data["chunk"]["state"] != "sls"
            and data["chunk"]["fun"] not in hub.idem.ccomps.invert.inversion_mapping
        ):
            new_unmets = set()
            for unmet in data["unmet"]:
                fun = unmet.split("_|-")[-1]
                if fun not in hub.idem.ccomps.invert.inversion_mapping:
                    new_unmets.add(unmet)
            data["unmet"] = new_unmets
            continue
        if data["unmet"]:
            new_chunk = {}
            for key, val in data["chunk"].items():
                if (
                    key == "name"
                    or key == "sls_sources_path"
                    or key == "acct_profile"
                    or key in hub.idem.rules.init.STATE_INTERNAL_KEYWORDS
                ):
                    new_chunk[key] = val
            data["chunk"] = new_chunk
        tag = data["tag"]
        for unmet in data["unmet"]:
            ind = tag_state_map[unmet]
            data_ind = tag_state_map[tag]
            if ind not in unmets:
                unmets[ind] = set()
            if data_ind not in unmets:
                unmets[data_ind] = set()
            tag_state = unmet.split("_|-")[0]
            # If any state requires acct profile, dependencies should not be inverted,
            # same acct_profile is required for both present and absent states. so we keep the acct require as it is
            # without inverting.
            if tag_state == "acct":
                unmets[data_ind].add(unmet)
            else:
                unmets[ind].add(tag)
        data["unmet"] = set()

    for ind, unmet in unmets.items():
        seq[ind]["unmet"] = unmet

    return seq
