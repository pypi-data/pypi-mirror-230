import asyncio
import re
from typing import Any
from typing import Dict

import jmespath
import pop.hub
import pop.loader


async def run(
    hub,
    desc_glob: str = "*",
    acct_file: str = None,
    acct_key: str = None,
    acct_profile: str = None,
    progress: bool = False,
    search_path: str = None,
    hard_fail: bool = False,
    output: str = None,
) -> Dict[str, Dict[str, Any]]:
    """
    :param hub:
    :param desc_glob: A glob or ref for which to run describe operations
    :param acct_file: The credential's file
    :param acct_key: The encryption key for the credential's file
    :param acct_profile: The credential profile to use
    :param progress: Show a progress bar
    :param search_path: A JMESpath to match to the results
    :param hard_fail: Raise an error and stop all describe operations when an exception is caught
    :param output: The render plugin to use for output
    :return:
    """
    result = {}
    coros = [
        _
        async for _ in hub.idem.describe.recurse(
            hub.states, desc_glob, acct_file, acct_key, acct_profile, dyne="state"
        )
    ]

    if len(coros) == 0:
        # The current approach is to recurse through all loaded resources types.
        # If it reaches here, it should have gone through all possible resource types when looking up
        # Do not fail but instead log it, do not return from here as there might be 'auto_state' to process
        hub.log.warning(
            f"Cannot find anything to describe for resource type(s) '{desc_glob}'"
        )

    # This is going through dynamically generated states for exec modules
    # implementing __contracts__ = ["auto_state"]
    async for coro in hub.idem.describe.recurse(
        mod=hub.exec,
        glob=desc_glob,
        acct_file=acct_file,
        acct_key=acct_key,
        acct_profile=acct_profile,
        dyne="exec",
    ):
        coros.append(coro)

    if len(coros) == 0:
        # If there is none to process including 'auto_state', there is no progress to show. Return empty result
        return result

    # Create the progress bar
    progress_bar = hub.tool.progress.init.create(coros)

    for ret in asyncio.as_completed(coros):
        hub.tool.progress.init.update(progress_bar)
        try:
            result.update(await ret)
        except Exception as e:
            hub.log.error(f"Error during describe: {e.__class__.__name__}: {e}")
            if hard_fail:
                raise
    if progress:
        progress_bar.close()
    if search_path:
        prepped = hub.output.jmespath.prepare(result)
        searched = jmespath.search(search_path, prepped)
        if output == "jmespath":
            # Don't post-process the result, it's already in jmespath format
            return searched
        else:
            return hub.output.jmespath.revert(searched)
    return result


async def recurse(
    hub,
    mod: pop.loader.LoadedMod or pop.hub.Sub,
    glob: str,
    acct_file: str,
    acct_key: str,
    acct_profile: str,
    ref: str = "",
    dyne: str = None,
):
    """
    :param hub:
    :param mod: A loaded mod or a sub on the hub
    :param glob: A glob or ref for which to run describe operations
    :param acct_file: The credential's file
    :param acct_key: The encryption key for the credential's file
    :param acct_profile: The credential profile to use
    :param ref: The current ref on the hub that is being examined for the proper contracts
    :param dyne: Either "exec" or "state" to keep track of which dyne is being recursed
    """
    if hasattr(mod, "_subs"):
        for sub in mod._subs:
            if ref:
                r = ".".join([ref, sub])
            else:
                r = sub
            async for c in hub.idem.describe.recurse(
                mod=mod[sub],
                glob=glob,
                acct_file=acct_file,
                acct_key=acct_key,
                acct_profile=acct_profile,
                ref=r,
                dyne=dyne,
            ):
                yield c
    if hasattr(mod, "_loaded"):
        for loaded in mod._loaded:
            if ref:
                r = ".".join([ref, loaded])
            else:
                r = loaded
            async for c in hub.idem.describe.recurse(
                mod=mod[loaded],
                glob=glob,
                acct_file=acct_file,
                acct_key=acct_key,
                acct_profile=acct_profile,
                ref=r,
                dyne=dyne,
            ):
                yield c

    if not re.fullmatch(glob, ref):
        return

    # Only describe functions that implement the "describe" contract
    if not hasattr(mod, "__contracts__"):
        if hasattr(mod, "_funcs") and "describe" in mod._funcs:
            hub.log.error(f"Implement the resource contract for '{ref}'.")
        else:
            hub.log.trace(f"No resource or auto_state contracts for {ref}")
        return

    if dyne == "exec":
        if "auto_state" not in mod.__contracts__:
            hub.log.trace(f"No auto_state contract for {ref}")
            return
        # Handle auto state describe functions
        ctx = await hub.idem.acct.ctx(
            path=glob,
            acct_file=acct_file,
            acct_key=acct_key,
            profile=acct_profile,
            hard_fail=True,
            validate=True,
        )
        ctx.exec_mod_ref = ref
        coro = hub.states.auto_state.describe(ctx)
        yield hub.pop.Loop.create_task(coro)
    elif dyne == "state":
        if "resource" not in mod.__contracts__:
            hub.log.trace(f"No resource contract for {ref}")
            return
        ctx = await hub.idem.acct.ctx(
            path=ref,
            acct_file=acct_file,
            acct_key=acct_key,
            profile=acct_profile,
            hard_fail=True,
            validate=True,
        )
        coro = mod.describe(ctx)
        yield hub.pop.Loop.create_task(coro)
    else:
        raise ValueError(f"Unknown dyne for performing describe operations '{dyne}'")
