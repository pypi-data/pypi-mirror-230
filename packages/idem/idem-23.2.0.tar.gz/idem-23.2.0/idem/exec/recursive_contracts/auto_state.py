"""
If an exec module plugin implements this contract,
the same ref can be used to call the state functions "present", "absent", and "describe".
"""
from typing import Any
from typing import Dict


def sig_get(hub, ctx, *args, **kwargs) -> Dict[str, Any]:
    return {"result": True | False, "comment": "", "ret": None}


def sig_list(hub, ctx, *args, **kwargs) -> Dict[str, Any]:
    return {"result": True | False, "comment": "", "ret": None}


def sig_create(hub, ctx, *args, **kwargs) -> Dict[str, Any]:
    return {"result": True | False, "comment": "", "ret": None}


def sig_update(hub, ctx, *args, **kwargs) -> Dict[str, Any]:
    return {"result": True | False, "comment": "", "ret": None}


def sig_delete(hub, ctx, *args, **kwargs) -> Dict[str, Any]:
    return {"result": True | False, "comment": "", "ret": None}
