from typing import Dict
from typing import List

# We gather required absent states, since they will not be found in ESM
# It will result in a redundant call to 'absent' which will result in 'already absent'
REQUIRE_FILTER_OUT = [{"fun": "present"}]


def gather_low_items(
    hub,
    low: List[Dict],
    required: List[str],
    low_items: List[Dict],
    filter_out: List = None,
):
    """
    Recursively gather low items of 'required' declaration ids and their pre-requisites.
    Any required declaration id might be resolved to multiple resources,
    in case there are multiple resources under the same declaration id.
    We gather 'require' and 'arg_bind' and add them to low if they cannot be retrieved
    from ESM.
    :param low: low data
    :param required: list of declaration ids of requisites ('require')
    :param low_items: gathered required low items
    :param filter_out: filter to filter out low items (exclude)
    """
    if not required:
        return

    for req in required:
        # required may be a list of lists
        if isinstance(req, List):
            for list_req in req:
                gather_low_items(hub, low, list_req, low_items, filter_out)
                continue

        req_items = [item for item in low if item.get("__id__") == req]
        # Start filtering only after first iteration, when original item(s) are added
        if len(low_items) > 0 and filter_out:
            req_items = filter_out_(req_items, filters=filter_out)

        for req_item in req_items:
            # make sure low_items have no duplicates
            if req_item in low_items:
                continue
            else:
                low_items.append(req_item)

            if req_item.get("require"):
                for required in req_item.get("require"):
                    if not isinstance(required, dict):
                        raise Exception(
                            f"Invalid syntax for 'require': '{required}'. Expected syntax: <state type>: <state id>."
                        )
                    gather_low_items(
                        hub,
                        low,
                        list(required.values()),
                        low_items,
                        filter_out=REQUIRE_FILTER_OUT,
                    )
            if req_item.get("arg_bind"):
                req_ids = []
                for arg_bind in req_item.get("arg_bind"):
                    for key, values in arg_bind.items():
                        for value in values:
                            for req_id, val in value.items():
                                req_ids.append(req_id)
                gather_low_items(
                    hub, low, list(req_ids), low_items, filter_out=REQUIRE_FILTER_OUT
                )


def filter_out_(low_items: List[Dict], filters: List[Dict]) -> List[Dict]:
    # Filter out required low items that are resources (present)
    # as those will be retrieved from the ESM. But any others absent or exec/sleep/script
    # required will be executed
    if not low_items or not filters:
        return low_items

    new_low_items = []
    for item in low_items:
        match = False
        for f in filters:
            for key, value in f.items():
                if item.get(key) == value:
                    match = True
        if not match:
            new_low_items.append(item)

    return new_low_items
