from typing import Any
from typing import Dict
from typing import Tuple

import dict_tools.data
import pop.hub


async def run(
    hub,
    path: str,
    args: Tuple[Any],
    kwargs: Dict[str, Any],
    *,
    ctx=None,
    acct_file: str = None,
    acct_key: str = None,
    acct_blob: bytes = None,
    acct_profile: str = None,
    acct_data: Dict[str, Any] = None,
    rerun_data=None,
):
    if acct_profile is None:
        acct_profile = hub.acct.DEFAULT

    args = [a for a in args]

    resolved = hub.idem.ex.resolve(path)
    path = resolved["path"]
    func = resolved["func"]
    params = resolved["params"]

    if "ctx" in params:
        if not ctx:
            ctx = {}
        if rerun_data:
            ctx["rerun_data"] = rerun_data
        ctx = dict_tools.data.NamespaceDict(ctx)

        # Load acct profile if it's not already set in the ctx
        if not ctx.get("acct"):
            acct_ctx = await hub.idem.acct.ctx(
                path,
                acct_file=acct_file,
                acct_key=acct_key,
                profile=acct_profile,
                acct_blob=acct_blob,
                acct_data=acct_data,
                hard_fail=True,
                validate=True,
            )
            ctx.update(acct_ctx)
        if len(ctx) > 0:
            args.insert(0, ctx)

    # Handle param aliases for exec
    if not isinstance(func, pop.hub.ReverseSub):
        for param, aliases in getattr(func, "param_aliases", {}).items():
            for alias in aliases:
                if alias in kwargs:
                    kwargs[param] = kwargs.pop(alias)
                    break

    ret = func(*args, **kwargs)
    return await hub.pop.loop.unwrap(ret)


def resolve(hub, path: str):
    """
    Resolve the exec module path and return the function, params, and actual reference path
    """
    if not path.startswith("exec."):
        path = f"exec.{path}"

    func = hub[path]
    if isinstance(func, pop.hub.ReverseSub):
        params = func._resolve().signature.parameters
    else:
        params = func.signature.parameters
    return {"func": func, "params": params, "path": path}


async def single(hub, path: str, *args, **kwargs):
    acct_file = hub.OPT.acct.acct_file
    acct_key = hub.OPT.acct.acct_key
    acct_profile = hub.OPT.acct.get("acct_profile", hub.acct.DEFAULT)

    ret = await hub.idem.ex.run(
        path,
        args=args,
        kwargs=kwargs,
        acct_file=acct_file,
        acct_key=acct_key,
        acct_profile=acct_profile,
    )
    return ret
