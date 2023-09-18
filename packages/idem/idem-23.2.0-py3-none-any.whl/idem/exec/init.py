from typing import Any
from typing import List

import dict_tools.data as dict_data


class ExecReturnType(type):
    """
    Metaclass for ExecReturn so that its type can be validated
    """

    def __instancecheck__(self, other) -> bool:
        try:
            # Verify that we can access the keys that make up an Exec Return
            _ = other["result"]
            _ = other["ret"]
            _ = other["comment"]
            _ = other["ref"]
            # Verify that we can access the attributes that make up an Exec Return
            _ = other.result
            _ = other.ret
            _ = other.comment
            _ = other.ref
            # Verify that "result" can be cast as a bool
            _ = bool(other["result"])
            _ = bool(other.result)
            _ = bool(other)
            # Looks like an exec return to me!
            return True
        except:
            return False


class ExecReturn(dict_data.NamespaceDict, metaclass=ExecReturnType):
    def __init__(
        self,
        result: bool,
        ret: Any = None,
        comment: List[str] = None,
        ref: str = "",
        **kwargs
    ):
        """
        Exec Returns must have the keys of "result", "ret", and "comment".
        Any other values can be added to the namespace
        """
        if not isinstance(result, bool):
            raise ValueError("Got a non boolean value for exec return `result`")
        if not isinstance(ref, str):
            raise ValueError("Got a non string value for exec return `ref`")

        super().__init__(result=result, ret=ret, comment=comment, ref=ref, **kwargs)

    def __bool__(self):
        return bool(self.get("result"))
