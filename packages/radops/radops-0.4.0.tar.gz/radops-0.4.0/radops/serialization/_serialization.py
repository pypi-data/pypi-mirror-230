import inspect
from typing import Any, Callable, Dict, List

import numpy as np

import radops

from ._deserialization import deserializable, deserializable_classes

__all__ = ["serializable"]

# setup loaders for primitive data types
SIMPLE_SERIALIZERS = {
    bool: lambda x: x,
    int: lambda x: x,
    float: lambda x: x,
    str: lambda x: x,
    dict: lambda x: x,
    type(None): lambda x: x,
    np.ndarray: lambda x: x.tolist(),
}


def serialize(x: Any, **kwargs) -> Any:
    """Turns a data type into something JSON-serializable"""
    if isinstance(x, list) or isinstance(x, tuple):
        return [serialize(xx, **kwargs) for xx in x]
    if isinstance(x, dict):
        return {k: serialize(v, **kwargs) for k, v in x.items()}
    if type(x) in SIMPLE_SERIALIZERS:
        return SIMPLE_SERIALIZERS[type(x)](x)
    if not hasattr(x, "serialize_to_dict"):
        raise ValueError(f"unable to serialize object {x}")
    return x.serialize_to_dict(**kwargs)


def get_serialization_attributes(obj: Any) -> List[str]:
    if hasattr(obj, "__serialization_attributes__"):
        serialization_attributes = obj.__serialization_attributes__
    else:
        serialization_attributes = list(
            inspect.signature(obj.__init__).parameters
        )

    if hasattr(obj, "__ignore_for_serialization__"):
        serialization_attributes = [
            a
            for a in serialization_attributes
            if a not in obj.__ignore_for_serialization__
        ]
    return serialization_attributes


def serialize_to_dict(self: Any, **kwargs) -> Dict[str, Any]:
    """Turns a class into a JSON-serializable dictionary. This is used to define
    Serializable.serialize_to_dict and also to monkey patch, as an instance method,
    onto non-radops classes such as PyTorch classes.
    """
    constructor_params = inspect.signature(self.__init__).parameters

    serialization_attributes = get_serialization_attributes(self)

    ret_dict = {
        "#class_name": f"{self.__class__.__module__}.{self.__class__.__name__}"
    }
    if kwargs.get("add_version", True):
        ret_dict["#meta"] = {
            **ret_dict.get("#meta", {}),
            "radops_version": radops.__version__,
        }
    if kwargs.get("add_methods", True):
        methods = sorted(
            (
                fn.inference_name
                for fn in (
                    getattr(self.__class__, m) for m in dir(self.__class__)
                )
                if callable(fn) and hasattr(fn, "inference_name")
            )
        )
        if methods:
            ret_dict["#meta"] = {
                **ret_dict.get("#meta", {}),
                "methods": methods,
            }

    for attr_name in serialization_attributes:
        if (
            attr_name not in constructor_params
            and inspect.getfullargspec(self.__init__).varkw is None
        ):
            raise RuntimeError(
                f"attribute name '{attr_name}' is in {self.__class__}.__serialization_attributes__ "
                f"but is not a parameter of {self.__class__}'s constructor"
            )

        attr = getattr(self, attr_name)

        # if attr is the default value, don't bother serializing it
        if (
            attr_name in constructor_params
            and constructor_params[attr_name].default is attr
        ):
            continue
        if "add_version" not in kwargs:
            # this way due to recursive calls
            kwargs["add_version"] = False
        ret_dict[attr_name] = serialize(attr, **kwargs)

    return ret_dict


def dedup_doc(cls):
    """
    Removes duplicated parameters in cls.__doc__
    """
    attribute_break = "----------"
    doc_parts = cls.__doc__.split(attribute_break)
    if (
        len(doc_parts) == 2
        and doc_parts[1] != ""
        and doc_parts[0][-15:] == "Parameters\n    "
    ):
        attribute_lines = doc_parts[1].split("\n    ")
        assert attribute_lines[0] == attribute_lines[-1] == ""
        # find attribute names, group them with descriptions
        name_idxs = []
        for i, line in enumerate(attribute_lines):
            if len(line) > 0 and line[0] != " ":
                name_idxs.append(i)
        name_idxs.append(len(attribute_lines) - 1)
        parts = [
            attribute_lines[name_idxs[i] : name_idxs[i + 1]]
            for i in range(len(name_idxs) - 1)
        ]
        # dedup parts
        for i in range(len(parts))[::-1]:
            if parts[i][0] in [x[0] for x in parts[:i]]:
                parts = parts[:i] + parts[i + 1 :]
        # put attributes back together
        attribute_lines = (
            [""] + [line for part in parts for line in part] + [""]
        )
        doc_parts[1] = "\n    ".join(attribute_lines)
    cls.__doc__ = attribute_break.join(doc_parts)
    return cls


def update_doc(cls):
    """
    Updates cls.__doc__ to include parameters from cls.__base__
    """
    attribute_break = "----------"
    remaining_attributes = []
    parent_classes = cls.__bases__
    for parent in parent_classes:
        if hasattr(parent, "__doc__") and parent.__doc__ is not None:
            split_parent_doc = parent.__doc__.split(attribute_break)
            if (
                len(split_parent_doc) >= 2
                and split_parent_doc[0][-15:] == "Parameters\n    "
            ):
                remaining_attributes.append(split_parent_doc[1])
    if remaining_attributes == []:
        return cls
    if cls.__doc__ is None:
        cls.__doc__ = ""
    if attribute_break not in cls.__doc__:
        cls.__doc__ = cls.__doc__ + "\n\n    Parameters\n    ----------"
    cls.__doc__ = cls.__doc__ + "\n".join(remaining_attributes)
    cls = dedup_doc(cls)
    return cls


def serializable(
    cls=None,
    override=False,
    serialize_to_dict_method: Callable = None,
    use_attrs: bool = True,
    load_from_config_dict_method: Callable = None,
):
    """Used as a decorator to make classes serializable.

    (Used hack described here: https://stackoverflow.com/a/60832711 so it can be used
    with or without arguments)
    """

    assert isinstance(cls, type) or cls is None

    def decorator(cls_):
        if cls_ not in deserializable_classes:
            cls_ = deserializable(
                cls_,
                use_attrs=use_attrs,
                override=override,
                load_from_config_dict_method=load_from_config_dict_method,
            )
        if not hasattr(cls_, "serialize_to_dict") or override:
            cls_.serialize_to_dict = (
                serialize_to_dict_method or serialize_to_dict
            )
        # TODO: figure out why update_doc is now broke
        # ret = update_doc(ret)

        return cls_

    return decorator if cls is None else decorator(cls)
