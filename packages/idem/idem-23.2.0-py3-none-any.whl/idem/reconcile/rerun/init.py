from typing import List


async def gather(hub, ctx, name: str, pending_tags: List = None):
    low = hub.idem.RUNS[name].get("low")

    # Getting 'rerun_data' from all tags.
    # 'rerun_data' is a metadata passed between re-runs.
    rerun_data_map = {}
    for tag in pending_tags:
        if hub.idem.RUNS[name]["running"][tag].get("rerun_data"):
            rerun_data_map[tag.split("_|-")[1]] = hub.idem.RUNS[name]["running"][
                tag
            ].get("rerun_data")

    # Clearing previous running data.
    hub.idem.RUNS[name]["running"] = {}
    pending_declaration_ids = [tag.split("_|-")[1] for tag in pending_tags]

    # Gather the states that are corresponding to the pending tags,
    # and the 'require' dependencies that are not resources:
    # such as time.sleep or data.write, exec or acct.profile.
    low_items = []
    hub.tool.idem.low_utils.gather_low_items(
        low=low,
        required=pending_declaration_ids,
        low_items=low_items,
        filter_out=None,
    )

    for key, rerun_data in rerun_data_map.items():
        for item in low_items:
            if item.get("__id__") == key:
                item["rerun_data"] = rerun_data

    return low_items
