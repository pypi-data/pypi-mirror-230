from typing import Any
from typing import Dict
from typing import Tuple


def previous_version(hub) -> Tuple[int, int, int]:
    return 1, 0, 0


def apply(hub, esm_cache: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upgrade from esm version 1.0.0 to 2.0.0
    """
    new_to_old_tags = {}
    no_upgrade_tags = []
    # Convert the tag to the new format and make sure there is only one object in ESM with this tag
    for tag in esm_cache.keys():
        if tag == hub.idem.managed.ESM_METADATA_KEY:
            continue
        resource_type, declaration_id, resource_name, _ = tag.split("_|-", maxsplit=3)
        new_tag = f"{resource_type}_|-{declaration_id}_|-{declaration_id}_|-"
        if tag == new_tag:
            no_upgrade_tags.append(tag)
            continue
        if not new_to_old_tags.get(new_tag, None):
            new_to_old_tags[new_tag] = []
        new_to_old_tags[new_tag].append(tag)

    hub.log.debug(f"Will upgrade esm for tags '{new_to_old_tags.keys()}'.")
    hub.log.debug(f"Tags that do not need upgrade '{no_upgrade_tags}'.")

    for new_tag, old_tags in new_to_old_tags.items():
        if len(old_tags) == 1:
            old_tag = old_tags.pop()
            # If there is only one chunk in ESM cache that matches the tag, migrate the chunk to the new tag
            esm_cache[new_tag] = esm_cache.pop(old_tag)
            hub.log.debug(
                f"Resource upgraded in ESM from tag '{old_tag}' to tag '{new_tag}'."
            )
        else:
            # Otherwise, skip migration
            hub.log.warning(
                f"Cannot upgrade resources in ESM '{old_tags}' to new tag '{new_tag}'."
            )

    # Get the metadata from the esm file cache
    metadata = esm_cache.get(hub.idem.managed.ESM_METADATA_KEY) or {}

    # Modify the esm_version in the metadata
    metadata["version"] = (2, 0, 0)

    # Apply the change to the esm file cache
    esm_cache[hub.idem.managed.ESM_METADATA_KEY] = metadata

    return esm_cache
