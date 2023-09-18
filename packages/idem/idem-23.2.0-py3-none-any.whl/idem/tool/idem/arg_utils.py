import dataclasses
from typing import _GenericAlias

import dict_tools
from dict_tools.typing import is_computed


def get_type_info_for_dataclass(hub, param_type) -> dict:
    # Return dictionary with the default values for a dataclass argument
    # Otherwise an empty dictionary
    dataclass_type_info = {}
    if dataclasses.is_dataclass(param_type):
        _dataclass_annotation_recursive(dataclass_type_info, param_type)
    elif (
        isinstance(param_type, _GenericAlias)
        and isinstance(param_type.__args__, tuple)
        and dataclasses.is_dataclass(param_type.__args__[0])
    ):
        _dataclass_annotation_recursive(dataclass_type_info, param_type.__args__[0])

    return dataclass_type_info


def calculate_changes(hub, old_state, new_state, params, func_ref) -> dict:
    # Calculate resource changes skipping values of Computed parameters

    computed_params = {}

    # Step 1: Get function parameters that are marked Computed, including nested parameters
    for name, param in params.items():
        if is_computed(param.annotation):
            computed_params[name] = None
        elif dataclasses.is_dataclass(param.annotation):
            computed_param_nested = _get_computed_params_nested_dataclass(
                param.annotation
            )
            if computed_param_nested:
                computed_params[param.name] = computed_param_nested
        elif (
            isinstance(param.annotation, _GenericAlias)
            and isinstance(param.annotation.__args__, tuple)
            and dataclasses.is_dataclass(param.annotation.__args__[0])
        ):
            computed_param_nested = _get_computed_params_nested_dataclass(
                param.annotation.__args__[0]
            )
            if computed_param_nested:
                computed_params[param.name] = computed_param_nested

    # Step 2: Calculate recursive diff of old_state and new_state ignoring changes in Computed values
    if computed_params:
        hub.log.info(
            f"Calculating changes for resource function '{func_ref}', ignoring Computed parameters [{computed_params}]."
        )
    changes = dict_tools.data.recursive_diff(
        old_state if old_state else dict(),
        new_state if new_state else dict(),
        ignore_keys_dict=computed_params,
        ignore_order=True,
    )

    return changes


def validate_param_dataclass(hub, dataclass_info: dict, value, missing_args: list):
    """
    This method sets default values in dataclass fields and detects
    missing required field values for function arguments of type dataclass

    :param dataclass_info: dataclass field information, includes default values and required fields
    :param value: the value for the argument as given, will be populated with default values
    :param missing_args: list of missing arguments
    """
    if dataclass_info is None:
        return

    if isinstance(value, list):
        for elem in value:
            _validate_param_dataclass(dataclass_info, elem, missing_args)
    else:
        _validate_param_dataclass(dataclass_info, value, missing_args)


def _validate_param_dataclass(
    dataclass_info: dict, elem: dict or list, missing_args: list = []
):
    # Recursive method for populating dataclass default values and detecting missing arguments
    if dataclass_info is None:
        return
    if elem is None:
        return
    if not isinstance(elem, list):
        for field_name, field_info in dataclass_info.items():
            if field_info is None:
                continue
            if field_info == "REQUIRED" and field_name not in elem:
                missing_args.append(field_name)
            elif field_name not in elem and not isinstance(field_info, dict):
                elem[field_name] = field_info
            elif isinstance(field_info, dict):
                _validate_param_dataclass(
                    field_info, elem.get(field_name), missing_args
                )
    else:
        for item in elem:
            _validate_param_dataclass(dataclass_info, item, missing_args)


def _dataclass_annotation_recursive(defaults, param_annotation):
    # Populate the default values of an argument of type dataclass
    # from the parameter annotation
    for field in dataclasses.fields(param_annotation):
        if dataclasses.is_dataclass(field.type):
            defaults[field.name] = {}
            _dataclass_annotation_recursive(defaults[field.name], field.type)
        elif (
            isinstance(field.type, _GenericAlias)
            and isinstance(field.type.__args__, tuple)
            and dataclasses.is_dataclass(field.type.__args__[0])
        ):
            defaults[field.name] = {}
            _dataclass_annotation_recursive(
                defaults[field.name], field.type.__args__[0]
            )
        elif isinstance(field.default, dataclasses._MISSING_TYPE):
            defaults[field.name] = "REQUIRED"
        elif field.default is not None:
            defaults[field.name] = field.default


def _get_computed_params_nested_dataclass(param_annotation):
    computed_params = {}

    for field in dataclasses.fields(param_annotation):
        if is_computed(field.type):
            computed_params[field.name] = None
        elif dataclasses.is_dataclass(field.type):
            computed_param_nested = _get_computed_params_nested_dataclass(field.type)
            if computed_param_nested:
                computed_params[field.name] = computed_param_nested

    return computed_params if len(computed_params) > 0 else None
