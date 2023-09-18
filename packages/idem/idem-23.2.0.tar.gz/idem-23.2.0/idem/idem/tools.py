import copy
import fnmatch
import inspect
import warnings
from typing import Any
from typing import Dict
from typing import List


def gen_chunk_func_tag(hub, chunk):
    """
    Generate the unique tag used to track the execution of the chunk
    """
    tag = _gen_tag(chunk)
    if hub.idem.ccomps.arg_bind.ARG_REFERENCE_REGEX_PATTERN.search(tag):
        hub.log.debug(
            f"Generated tag '{tag}' include argument binding syntax. The tag will change once the requisites are "
            "resolved for the state"
        )
    return f'{tag}{chunk["fun"]}'


def gen_chunk_esm_tag(hub, chunk: Dict[str, str]) -> str:
    """
    Generate the unique tag used to track the execution of the chunk in the esm
    """
    return _gen_tag(chunk)


def _gen_tag(chunk: Dict[str, str]) -> str:
    """
    Generate the unique tag used to track the execution of the chunk

    This will be used at a module level, agnostic to function names
    """
    chunk_state = chunk["state"]
    chunk_id = chunk["__id__"]
    # If resource_name is not set, use chunk id
    chunk_resource_name = (
        chunk.get("resource_name") if chunk.get("resource_name") else chunk_id
    )
    tag = f"{chunk_state}_|-{chunk_id}_|-{chunk_resource_name}_|-"

    return tag


def tag_2_state(hub, tag):
    # Get state from the tag
    return tag[0 : tag.find("_|")]


def get_chunks(hub, low, state, name, resource_name: str = None):
    """
    Search in the low state for the chunk with the given designation
    Resource_name is optional, but if defined should match.
    """
    rets = []
    for chunk in low:
        if state == "sls":
            if fnmatch.fnmatch(chunk["__sls__"], name):
                rets.append(chunk)
                continue
        if state == chunk["state"]:
            if fnmatch.fnmatch(chunk["__id__"], name) or fnmatch.fnmatch(
                chunk["name"], name
            ):
                if resource_name is None or resource_name == chunk["resource_name"]:
                    rets.append(chunk)
    return rets


def find_name(hub, name, state, high):
    """
    Scan high data for the id referencing the given name and return a list of (IDs, state) tuples that match
    Note: if `state` is sls, then we are looking for all IDs that match the given SLS
    """
    ext_id = []
    if name in high:
        ext_id.append((name, state))
    # if we are requiring an entire SLS, then we need to add ourselves to everything in that SLS
    elif state == "sls":
        for nid, item in high.items():
            if item["__sls__"] == name:
                ext_id.append((nid, next(iter(item))))
    # otherwise we are requiring a single state, lets find it
    else:
        # We need to scan for the name
        for nid in high:
            if state in high[nid]:
                if isinstance(high[nid][state], list):
                    for arg in high[nid][state]:
                        if not isinstance(arg, dict):
                            continue
                        if len(arg) != 1:
                            continue
                        if arg[next(iter(arg))] == name:
                            ext_id.append((nid, state))
    return ext_id


def format_call(
    hub,
    fun,
    data,
    ignore_changes: List = None,
    expected_extra_kws=(),
    enforced_state: Dict[str, Any] = None,
):
    """
    Build the required arguments and keyword arguments required for the passed
    function.
    :param fun: The function to get the argspec from
    :param data: A dictionary containing the required data to build the
                 arguments and keyword arguments.
    :param ignore_changes: A list of path of parameters that will be assigned to None value
                           to ignore being updated in present().
    :param expected_extra_kws: Any expected extra keyword argument names which
                               should not trigger a :ref:`SaltInvocationError`
    :param enforced_state: A dictionary with the parameters from a previous run
    :returns: Function keyword arguments.
    """
    enforced_state = enforced_state or {}

    args = []
    kwargs = {}
    keywords = False
    # Map of param name to param info for dataclasses, info includes whether the field is required or has a default value
    dataclass_args = {}
    # Since we WILL be changing the data dictionary, let's change a copy of it
    data = data.copy()

    sig = fun.signature

    # Handle param aliases for idem
    for param, aliases in getattr(fun, "param_aliases", {}).items():
        for alias in aliases:
            if alias in data:
                data[param] = data.pop(alias)
                break

    for name, param in sig.parameters.items():
        if name == "hub":
            continue
        elif param.kind.name == "POSITIONAL_OR_KEYWORD":
            param_dataclass_info = hub.tool.idem.arg_utils.get_type_info_for_dataclass(
                param.annotation
            )
            if param_dataclass_info:
                dataclass_args.update({name: param_dataclass_info})
            if param.default is inspect._empty:
                if name in enforced_state:
                    # get it from enforced state before state
                    kwargs[name] = enforced_state[name]
                else:
                    # Warn about required argument that is not stored in ESM
                    if enforced_state and name != "ctx" and name != "name":
                        msg = (
                            f"Function {fun.ref}.{fun.func.__name__} argument '{name}' is required, "
                            f"but is not found in ESM cache for {gen_chunk_func_tag(hub, data)}"
                        )
                        warnings.warn(msg, RuntimeWarning)
                        hub.log.warning(msg)
                    args.append(name)
            else:
                kwargs[name] = enforced_state.get(name, param.default)
                # Validate a boolean value for arguments of type boolean
                if isinstance(param.default, bool):
                    if data.get(name) and not isinstance(data.get(name), bool):
                        raise TypeError(
                            f"{fun.ref}.{fun.func.__name__} is expecting a boolean value for '{name}'"
                            f" but got '{data.get(name)}'"
                        )
        elif param.kind.name == "KEYWORD_ONLY":
            # get it from enforced state before default
            kwargs[name] = enforced_state.get(name, param.default)
        elif param.kind.name == "VAR_KEYWORD":
            keywords = True

    is_existing_resource = bool(enforced_state) or bool(data.get("resource_id"))

    missing_args = []

    for key in kwargs:
        try:
            # Value from request
            val = data.pop(key)

            if key == "resource_id":
                # if the execution flow is for recreating a resource,
                # then we should override enforced_state value with None for resource_id
                if data.get("recreation_flow", False):
                    kwargs[key] = val
                    continue

                # If resource_id in SLS is set to an empty string, make sure it does not override the
                # value in ESM, as it will cause the resource to be recreated during reconciliation
                if val is None or (isinstance(val, str) and not val.strip()):
                    continue

            # If 'name' is not set in SLS but set in ESM, get it from ESM
            if (
                key == "name"
                and val == data["__id__"]
                and enforced_state["name"] is not None
                and enforced_state["name"] != val
            ):
                kwargs[key] = enforced_state["name"]

            # Do not override enforced_state value with None,
            # unless no value is set
            elif val is not None or kwargs[key] is inspect._empty:
                kwargs[key] = val

            # Populate default values for dataclasses
            if key in dataclass_args:
                hub.tool.idem.arg_utils.validate_param_dataclass(
                    dataclass_args.get(key), val, missing_args
                )

        except KeyError:
            # Let's leave the default value in place
            pass

    # If ignore_changes contains parameters, then we try to assign those parameters with None to skip updating.
    # For resource recreation flow, we should not nullify the parameters in ignore_changes.
    if (
        ignore_changes
        and is_existing_resource
        and not data.get("recreation_flow", False)
    ):
        hub.idem.tool.ignore_changes.ignore_parameter_changes(
            ignore_changes=ignore_changes,
            params=kwargs,
            param_signatures=sig.parameters,
        )

    while args:
        # Every function takes ctx as an argument.
        # All others are required function arguments that do not exist in ESM
        arg = args.pop(0)
        try:
            kwargs[arg] = data.pop(arg)
        except KeyError:
            missing_args.append(arg)

    if missing_args:
        raise ValueError(
            f"{fun.ref}.{fun.func.__name__} is missing required argument(s): {', '.join(missing_args)}"
        )

    if keywords:
        # The function accepts **kwargs, any non expected extra keyword
        # arguments will made available.
        for key, value in data.items():
            if key in expected_extra_kws:
                continue
            kwargs[key] = value

        # No need to check for extra keyword arguments since they are all
        # **kwargs now. Return
        return kwargs

    # Did not return yet? Lets gather any remaining and unexpected keyword
    # arguments
    extra = {}
    for key, value in data.items():
        if key in expected_extra_kws:
            continue
        extra[key] = copy.deepcopy(value)

    if extra:
        # Found unexpected keyword arguments, raise an error to the user
        if len(extra) == 1:
            msg = "'{0[0]}' is an invalid keyword argument for '{1}'".format(
                list(extra.keys()), f"{fun.__module__}.{fun.__name__}"
            )
        else:
            msg = "{} and '{}' are invalid keyword arguments for '{}'".format(
                ", ".join([f"'{e}'" for e in extra][:-1]),
                list(extra.keys())[-1],
                f"{fun.__module__}.{fun.__name__}",
            )
        warnings.warn(msg, RuntimeWarning)
        hub.log.warning(msg)
    return kwargs


def ishashable(hub, obj):
    """
    A simple test to verify if a given object is hashable and can therefore
    be used as a key in a dict
    """
    try:
        hash(obj)
    except TypeError:
        return False
    return True


def iter_high(hub, high):
    """
    Take a high-state structure and iterate over it yielding the elements down to the
    execution args
    Yields (id_, body, state, run, arg)
    """
    for id_, body in high.items():
        if not isinstance(body, dict):
            continue
        for state, run in body.items():
            if state.startswith("__"):
                continue
            for arg in run:
                yield id_, body, state, run, arg


def iter_high_leaf_args(hub, high):
    """
    Take a high-state structure and iterate over it yielding the elements down to the
    execution args
    Yields (id_, body, state, run, arg)
    """
    for id_, body in high.items():
        if not isinstance(body, dict):
            continue
        for state, run in body.items():
            if state.startswith("__"):
                continue
            for arg in run:
                yield from _iter_arg_chain(id_, body, state, run, "", arg)


def _iter_arg_chain(id_, body, state, run, arg_key_def, arg):
    if isinstance(arg, dict):
        for arg_key, arg_value in arg.items():
            # Escape dictionary references in the key definition to skip evaluating by arg_bind resolver.
            arg_key = arg_key.replace("[", "[\\")
            if arg_key_def:
                current_arg_key_def = arg_key_def + ":" + arg_key
            else:
                current_arg_key_def = arg_key

            if isinstance(arg_value, dict):
                yield from _iter_arg_chain(
                    id_, body, state, run, current_arg_key_def, arg_value
                )
            elif isinstance(arg_value, list):
                for index, arg_value_item in enumerate(arg_value):
                    yield from _iter_arg_chain(
                        id_,
                        body,
                        state,
                        run,
                        current_arg_key_def + f"[{index}]",
                        arg_value_item,
                    )
            else:
                yield id_, body, state, run, current_arg_key_def, arg_value
    elif isinstance(arg, list):
        for index, arg_value_item in enumerate(arg):
            yield from _iter_arg_chain(
                id_, body, state, run, arg_key_def + f"[{index}]", arg_value_item
            )
    else:
        yield id_, body, state, run, arg_key_def, arg


def get_enforced_state(hub, chunk, managed_state):
    tag = hub.idem.tools.gen_chunk_func_tag(chunk)
    esm_tag = hub.idem.tools.gen_chunk_esm_tag(chunk)
    new_chunk = {**chunk, "__id__": f"{chunk['__id__']}_create_new"}
    new_tag = hub.idem.tools.gen_chunk_func_tag(new_chunk)
    new_esm_tag = hub.idem.tools.gen_chunk_esm_tag(new_chunk)

    enforced_state = managed_state.get(new_esm_tag) or managed_state.get(new_tag)

    if not enforced_state:
        enforced_state = managed_state.get(esm_tag) or managed_state.get(tag)

    return enforced_state


def format_dict_return_type_for_missing_keys(hub):
    """
    Jinja render uses the params python dict object to read the value corresponding to
    any parameter. When the parameter is not present params dict object's get() returns
    the None object. We need to return __PYTHON_NONE__ instead, so that it gets suitably
    converted into the python None object in the replacement renderer.
    Here we are using type library function to create a new type object, that has get()
    function which returns self[key] if parameter (key) is present, default value (if
    specified), and __PYTHON_NONE__ otherwise. Python dict is used as base class.
    Thus, for all parameters that are not present in dict, this get() lambda returns
    __PYTHON_NONE__.
    """
    return type(
        "",
        (dict,),
        {
            "get": lambda self, key, value=None: self[key]
            if key in self
            else value
            if value is not None
            else "__PYTHON_NONE__"
        },
    )()
