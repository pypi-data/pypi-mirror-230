from typing import List

import pytest

from radops.serialization import serializable
from radops.serialization._math import exhibit_cycle


def test_exhibit_cycle_pos():
    nodes = [1, 2, 3]
    edges = [(1, 2), (1, 3), (2, 3), (3, 1)]

    assert exhibit_cycle(nodes, edges) == [1, 2, 3, 1]


def test_exhibit_cycle_neg():
    nodes = [1, 2, 3]
    edges = [(1, 2), (1, 3)]

    assert exhibit_cycle(nodes, edges) is None


def test_nested_deserialization():
    @serializable
    class A:
        x: List[int]

    @serializable
    class B:
        a: A
        d: dict

    @serializable
    class C:
        b: B
        n: int
        s: str

    c = C.load_from_config_dict(
        {
            "b": {"a": {"x": [3, 8]}, "d": {"k": "v"}},
            "n": "#b.a.x.0",
            "s": "#b.d./k/",
        }
    )
    assert c.n == 3
    assert c.s == "v"

    d = c.serialize_to_dict()
    assert "#meta" in d
    d.pop("#meta")
    assert d == {
        "#class_name": "test_serialization.C",
        "b": {
            "#class_name": "test_serialization.B",
            "a": {"#class_name": "test_serialization.A", "x": [3, 8]},
            "d": {"k": "v"},
        },
        "n": 3,
        "s": "v",
    }


def test_casting():
    @serializable
    class A:
        n: int

    with pytest.warns() as record:
        a = A.load_from_config_dict({"n": 1.0})
    assert isinstance(a.n, int)
    assert a.n == 1

    assert len(record) == 1
    assert "casting to the expected" in str(record[0].message)

    d = a.serialize_to_dict()
    assert "#meta" in d
    d.pop("#meta")
    assert d == {"n": 1, "#class_name": "test_serialization.A"}
