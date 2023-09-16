# Serialization module

## Examples

Below are a bunch of examples of the serialziation module. These are all automatically tested as working via [doctest](https://docs.python.org/3/library/doctest.html). Note in the below examples we ignore the `#meta`
key (whose value stores the `radops` version) when dispalying the result for reproducibility with `doctest`.

### Basic (de)serialization examples

```python
>>> from radops.serialization import serializable
>>> @serializable
... class A:
...     i: int
...     j: bool = True
>>> @serializable
... class B(A):
...     s: str = None
>>> @serializable
... class C:
...     a: A
>>> c = C.load_from_config_dict({"a": {"i": 7, "j": False}})
>>> isinstance(c.a, A)
True
>>> c.a.i, c.a.j
(7, False)
>>> c = C.load_from_config_dict({"a": {"#class_name": "B", "i": 3, "s": "a string"}})
>>> isinstance(c.a, B)
True
>>> c.a.i, c.a.s
(3, 'a string')
>>> serialized_dict = c.serialize_to_dict()
>>> print({k:v for k, v in serialized_dict.items() if k != "#meta"})
{'#class_name': '__main__.C', 'a': {'#class_name': '__main__.B', 'i': 3, 's': 'a string'}}

```

### Usage without `attrs`

Some classes do not play well with `attrs` and one such instance is `nn.Module` (due to PyTorch neededing these objects to be hashable but `attrs` refusing to allow a mutable object to be hashable). In this case, the `serializable` decorator should be used with the argument `use_attrs=False` argument.

```python
>>> @serializable(use_attrs=False)
... class D:
...     def __init__(self, r: str, i: int):
...         self.r = r
...         self.i = i
>>> d = D.load_from_config_dict({"r": "a", "i": -2})
>>> d.r, d.i
('a', -2)
>>> serialized_dict = d.serialize_to_dict()
>>> print({k:v for k, v in serialized_dict.items() if k != "#meta"})
{'#class_name': '__main__.D', 'r': 'a', 'i': -2}

```

### Specifying what attributes to use for serialization

By default, `serialize_to_dict` will serialize all attributes. There are some cases where
this is not desired (examples are the `device` parameter in the trainer classes or the `params`
parameter in `teddy.torch.Optimizer`). To explicitly set what attributes should be serialized, the
`__serialization_attributes__` attribute can be set.

```python
>>> @serializable
... class E:
...     __serialization_attributes__ = ["x", "z"]
...     x: int
...     y: str
...     z: bool
>>> e = E(1, "b", False)
>>> serialized_dict = e.serialize_to_dict()
>>> print({k:v for k, v in serialized_dict.items() if k != "#meta"})
{'#class_name': '__main__.E', 'x': 1, 'z': False}

```

Alternatively, attributes that should not be serialized can be specified instead via
the `__ignore_for_serialization__` attribute:

```python
>>> @serializable
... class F:
...     __ignore_for_serialization__ = ["y"]
...     x: int
...     y: str
...     z: bool
>>> f = F(1, "b", False)
>>> serialized_dict = f.serialize_to_dict()
>>> print({k:v for k, v in serialized_dict.items() if k != "#meta"})
{'#class_name': '__main__.F', 'x': 1, 'z': False}

```
