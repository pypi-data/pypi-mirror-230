import json
import tarfile
import tempfile
import typing
import warnings
from collections.abc import Generator
from importlib import import_module
from types import GeneratorType
from typing import Any, Callable, Dict, List, Set, Tuple, Union

import attr
import numpy as np

from ._math import top_sort

GenericType = typing._GenericAlias

# maintained list of classes that have been made deserializable
deserializable_classes = []


class DeserializeError(Exception):
    pass


def cast_loader(x: Any, type_: type) -> Any:
    """Loader that tries to cast input to specified type. Raises
    a ``DeserializeError`` if it cannot.
    """
    try:
        if isinstance(x, type_):
            return x
        ret = type_(x)
        warnings.warn(
            f"Received value of type {type(x)}, casting to the expected type {type_}."
        )
        return ret
    except Exception:
        raise DeserializeError(f"Cannot convert {x} to type {type_}.")


# setup loaders for primitive data types. In the case of ints and floats we
# explicitly cast since json has a single data type for numbers.
SIMPLE_LOADERS = {
    bool: lambda x: x,
    int: lambda x: cast_loader(x, int),
    float: lambda x: cast_loader(x, float),
    str: lambda x: x,
    dict: lambda x: x,
    GeneratorType: lambda x: x,
    Generator: lambda x: x,
    np.ndarray: lambda x: np.array(x),
}


def build_unresolved_dependency_graph(
    conf: Union[list, tuple, Dict[str, Any]]
):
    """
    Builds the dependency graph for a config: since some arguments may depend
    on others (via the special character "#"), it's important to load in the proper order.

    Parameters
    ----------
    conf
        configuration dict (or list of configuration dicts)

    Returns
    -------
    The return is a two-element list. The first element of the tuple is a tuple of edges
    giving the dependencies of the keys in the config dict. The second is a list of
    unresolved dependencies; these are argument which are called by the special character
    #, but are not loaded within the config dict. The config dict itself will depend on
    these arguments; they may arise as things loaded in a parent config dict.
    """
    edges = []
    unresolved_dependencies = []

    if isinstance(conf, list):
        for item in conf:
            _, deep_dependencies = build_unresolved_dependency_graph(item)
            unresolved_dependencies += deep_dependencies
    elif type(conf) == dict:
        for k, v in conf.items():
            if isinstance(v, str) and v != "" and v[0] == "#":
                dep = v[1:].split(".")[0]
                if dep in conf and dep != k:
                    edges.append((dep, k))
                else:
                    unresolved_dependencies.append(dep)
            elif (
                isinstance(v, list)
                or isinstance(v, tuple)
                or isinstance(v, dict)
            ):
                _, deep_dependencies = build_unresolved_dependency_graph(v)
                for dep in deep_dependencies:
                    if dep in conf:
                        edges.append((dep, k))
                    else:
                        unresolved_dependencies.append(dep)
            else:
                continue
    else:
        pass

    # Duplicates can appear when conf is a list.
    edges = tuple(set(edges))
    unresolved_dependencies = list(set(unresolved_dependencies))

    return [edges, unresolved_dependencies]


def build_dependency_graph(
    conf: Dict[str, Any]
) -> Tuple[Tuple[str, str], ...]:
    """Builds the dependency graph for a config: since some arguments may depend
    on others (via the special character "#") its important to load in the proper order.

    Parameters
    ----------
    conf
        configuration dict

    Returns
    -------
    The return is a tuple of tuples of keys from conf, where (str1, str2) means
    that conf[str2] depends on conf[str1].

    Examples
    --------
    >>> conf = {"a": {"i": 2}, "b": {"j": "#a.i"}, "c": 3}
    >>> build_dependency_graph(conf)
    (('a', 'b'),)

    In this example an edge is drawn between "a" and "b" since "b"
    has a dependency on a
    """
    return tuple(build_unresolved_dependency_graph(conf)[0])


def get_all_subclasses(cls: type) -> Set[type]:
    """Returns a list of subclasses.

    Parameters
    ----------
    cls
        The class to get the subclasses of

    Returns
    -------
    set of all subclasses of ``cls``. This includes those classes which are
    subclasses of subclasses of ``cls``.
    """
    ret = cls.__subclasses__()
    for subcls in ret:
        ret.extend(get_all_subclasses(subcls))
    return set(ret)


try:
    type_type = Union[type, typing._GenericAlias]
# typing._GenericAlias doesn't exist in python 3.6
except AttributeError:
    type_type = Any


def _get_origin(type_: GenericType) -> type:
    """Get origin of type. The method depends on the python version"""
    return type_.__origin__


def load(
    type_: type_type,
    c: Any,
    previous_levels: List[Dict[str, Any]] = None,
) -> Any:
    """Loads an object based on being passed its type and its value
    (e.g. for a primitive data type) or configuration dict (e.g. for a class
    defined in radops).

    Parameters
    ----------
    type_
        the type of the object. Can be a primitive data type or a class from
        the ``typing`` module such as Union or List.
    c
        the value or configuration dict to create the object from.
    previous_level
        optional dictionary from which data for the constructor of the to
        be created object can be retrieved.

    Returns
    -------
    the loaded object.
    """
    if previous_levels is None:
        previous_levels = []

    # check if type_ is one of typing.Union, typing.List, typing.Tuple, or typing.Dict
    # the or is need for typing.Union in python 3.6
    if isinstance(type_, GenericType) or (
        hasattr(type_, "__origin__") and type_.__origin__ == typing.Union
    ):
        # for typing.Union, recursively call this function on the types in the union
        if _get_origin(type_) == typing.Union:
            for t in type_.__args__:
                try:
                    return load(t, c, previous_levels)
                except DeserializeError:
                    pass

        # for typing.List, check that c is a list and then call this function
        # on the data type in the list and elements in c
        origin = _get_origin(type_)
        if origin == list:
            if not isinstance(c, list):
                raise DeserializeError(f"Expecting a list but got {c}")
            return [
                load(type_.__args__[0], cc, previous_levels=previous_levels)
                for cc in c
            ]

        # for typing.Dict, do the analogous thing as above.
        if origin == dict:
            if not isinstance(c, dict):
                raise DeserializeError(f"Expecting a dict but got {c}")
            if "#class_name" in c:
                raise DeserializeError(
                    f"Expecting a dict, but got {c['#class_name']}"
                )
            return {
                k: load(type_.__args__[1], v, previous_levels=previous_levels)
                for k, v in c.items()
            }

        # for typing.Tuple, check that c is a list and of the same size as
        # the arguments to typing.Tuple. then call this function on the types in
        # the tuple and elements in c
        if origin == tuple:
            if not isinstance(c, list):
                raise DeserializeError(f"Expecting a list but got {c}")

            if len(type_.__args__) != len(c):
                raise DeserializeError(
                    f"Expecting a list of length {len(type_.__args__)} but got a list of length {len(c)}"
                )
            return [
                load(t, cc, previous_levels=previous_levels)
                for t, cc in zip(type_.__args__, c)
            ]

        # for a dict verify that all specified types are taken care of
        # by SIMPLE_LOADERS and then load accordingly.
        if type_ == dict:
            assert all([t in SIMPLE_LOADERS for t in type_.__args__])
            type_ = dict
        # finally if all else fails try taking the type's origin as the type
        else:
            type_ = _get_origin(type_)

    # load simple data types
    if type_ in SIMPLE_LOADERS:
        return SIMPLE_LOADERS[type_](c)

    # load complex data types
    if hasattr(type_, "load_from_config_dict"):
        return type_.load_from_config_dict(c, previous_levels)

    # Handle typing generic types ~KT, ~VT
    if type_ == typing.TypeVar("VT") or type_ == typing.TypeVar("KT"):
        raise DeserializeError(
            "type hints missing from Dict. Be sure to specify the key,value types in Dict \
            (e.g. Dict[str,int] instead of Dict)"
        )
    raise DeserializeError(
        f"unable to load specified type {type_} with value {c}."
    )


def get_subclass(cls: type, subclass_name: str) -> type:
    """Get a subclass of a class.

    Parameters
    ----------
    cls
        the super class
    subclass_name
        the subclass to get. This can either be the name (i.e. the __name__ attribute)
        or it can be a string with dot notation (e.g. ``"torch.optim.Adam"``).

    Returns
    -------
    The found subclass
    """
    if "." in subclass_name:
        s = subclass_name.split(".")
        package_name = ".".join(s[:-1])
        return getattr(import_module(package_name), s[-1])

    # if the requested subclass is the class itself, return it
    if subclass_name == cls.__name__:
        return cls

    # otherwise get all subclasses of the class and search there for matching
    # class name. if there are multiple (e.g. two classes can have the same name
    # but be in different modules) then raise a value error and tell the user
    # to be more specific by using dot notation.
    subclasses = get_all_subclasses(cls)
    class_ = [c for c in subclasses if c.__name__ == subclass_name]
    if len(class_) > 1:
        raise ValueError(
            f"multiple subclasses with name {subclass_name} found: {class_}. "
            "Please use dot notation to specify exact class."
        )
    if len(class_) == 0:
        raise DeserializeError(
            f"Could not find {subclass_name} as a subclass of {cls}"
        )
    return class_[0]


def get_attr_recursive(cls: Any, attribute: List[str]) -> Any:
    """
    Get the attribute of cls described by the attribute list. E.g. if attribute = ['a','b','c'],
    then return cls.a.b.c. This also handles the edge cases of indexing, method calls, and keying (e.g.
    `b.0.c` or `a.b.c()` or `a./key/.c`)
    """

    def is_index(x):
        try:
            int(x)
            return True
        except ValueError:
            return False

    def is_key(x):
        if x[0] == "/" and x[-1] == "/":
            return True
        else:
            return False

    def is_method(x):
        if x[-2:] == "()":
            return True
        else:
            return False

    attribute_val = cls
    for x in attribute:
        if is_index(x):
            attribute_val = attribute_val[int(x)]
        elif is_method(x):
            attribute_val = getattr(attribute_val, x[:-2])()
        elif is_key(x):
            attribute_val = attribute_val[x[1:-1]]
        else:
            attribute_val = getattr(attribute_val, x)

    return attribute_val


def load_from_config_dict(
    cls: type,
    conf: Dict[str, Any],
    previous_levels: List[Dict[str, Any]] = None,
) -> Any:
    """Loads an object from a config dict

    Parameters
    ----------
    cls
        The class that the returned object is an instance of
    conf
        (JSON serializable) configuration dict
    previous_level
        a previous level of a configuration dict. This is to hold objects that
        are used as parameters of the return object's constructor. For example
        if previous_level has a key ``a`` and ``conf`` has the key-value pair
        ``b, #a.attr``, then ``previous_level[a].attr`` will be passed as the
        parameter ``b`` in ``cls.__init__`` (or ``sub_cls.__init__`` if
        ``conf`` contains key ``"#class_name"`` with value ``"sub_cls"``).


    Returns
    -------
    An instance of (a subclass of) cls.
    """
    if previous_levels is None:
        previous_levels = []

    # make a copy of conf without the "#meta" key
    conf = {k: v for k, v in conf.items() if k != "#meta"}

    # get the exact class to load in case it was passed explicitly via #class_name
    # and then call this method with that class.
    if "#class_name" in conf:
        class_ = get_subclass(cls, conf["#class_name"])
        return class_.load_from_config_dict(
            {k: v for k, v in conf.items() if k != "#class_name"},
            previous_levels,
        )

    if type(conf) == list or type(conf) == tuple:
        return [
            load_from_config_dict(cls, item, previous_levels=previous_levels)
            for item in conf
        ]

    # type_hints is a dict mapping the parameter names of the constructor
    # of cls to their typing hints
    type_hints = cls.__type_hints__
    # init_dict is the dictionary that will be passed to the constructor of cls
    # to build the return object
    previous_levels = [{}] + previous_levels
    # build the dependency graph and then sort it topologically, loading
    # in that order so that a dependency is always loaded before something
    # that depends on it.
    edges = build_dependency_graph(conf)
    ordered_keys = top_sort(list(conf.keys()), edges)
    for k in ordered_keys:
        v = conf[k]
        if isinstance(v, str) and v.startswith("#"):
            v = v[1:]
            s = v.split(".")
            attribute_found = False
            if len(s) == 1:
                for i in range(len(previous_levels)):
                    if s[0] in previous_levels[i] and (i != 0 or s[0] != k):
                        previous_levels[0][k] = previous_levels[i][s[0]]
                        attribute_found = True
                        break
                if not attribute_found:
                    raise NameError(f"The name {s[0]} was not found")
            else:
                key, attribute = s[0], s[1:]
                for i in range(len(previous_levels)):
                    if key in previous_levels[i] and (i != 0 or key != k):
                        try:
                            previous_levels[0][k] = get_attr_recursive(
                                previous_levels[i][key], attribute
                            )
                            attribute_found = True
                        except NameError:
                            pass
                if not attribute_found:
                    attribute_st = ".".join(attribute)
                    raise NameError(
                        f"The name {key}.{attribute_st} was not found."
                    )
        elif k in type_hints:
            previous_levels[0][k] = load(
                type_hints[k], v, previous_levels=previous_levels
            )
        else:
            previous_levels[0][k] = v
    try:
        return cls(**previous_levels[0])
    except TypeError as e:
        raise DeserializeError(
            f"Attempting to load class {cls} "
            + f"with config dict {conf} failed with the following error: {e}"
        )


def modify_statedict_path(conf: any, dirpath: str):
    """Replace all values of #state_dict_path in a config with dirpath + filename"""
    if not isinstance(conf, dict):
        return conf

    if "#state_dict_path" in conf:
        conf["#state_dict_path"] = (
            dirpath + "/" + conf["#state_dict_path"].split("/")[-1]
        )
        if "#bucket_name" in conf:
            conf.pop("#bucket_name")

    return {k: modify_statedict_path(v, dirpath) for k, v in conf.items()}


def load_from_tgz(cls: type, tarpath: str):
    """Load a from a tar.gz file that contains the config as 'config.json' and
    any other #state_dict_path objects referenced in the config (so they don't
    need to be grabbed from remote storage)

    Note: this doesn't verify that all the requisite state dict objects are in
    the tar.gz file. Also beware that if the config has a serializable_with_state_dict
    object that points to a bucket, this will modify the config to instead look
    inside the targz file.
    """

    with tempfile.TemporaryDirectory() as dirpath:
        tar = tarfile.open(tarpath)
        tar.extractall(dirpath)
        tar.close()

        try:
            config = json.load(open(dirpath + "/config.json", "r"))
        except FileNotFoundError as e:
            raise e("Tarfile must contain a 'config.json' file")

        config = modify_statedict_path(config, dirpath)
        return cls.load_from_config_dict(config)


def deserializable(
    cls=None,
    use_attrs: bool = True,
    override=False,
    load_from_config_dict_method: Callable = None,
):
    """Used as a decorator to make classes serializable.

    (Used hack described here: https://stackoverflow.com/a/60832711 so it can be used
    with or without arguments)
    """

    assert isinstance(cls, type) or cls is None

    def decorator(cls_):
        if use_attrs:
            ret = attr.s(cls_, auto_attribs=True, hash=True)
            ret.__type_hints__ = typing.get_type_hints(cls_)
        else:
            ret = cls_
            ret.__type_hints__ = typing.get_type_hints(cls_.__init__)
        if not hasattr(ret, "load_from_config_dict") or override:
            ret.load_from_config_dict = classmethod(
                load_from_config_dict_method or load_from_config_dict
            )
        ret.load_from_tgz = classmethod(load_from_tgz)

        deserializable_classes.append(cls_)

        return ret

    return decorator if cls is None else decorator(cls)
