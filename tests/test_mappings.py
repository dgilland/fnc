from collections import defaultdict, namedtuple

import pytest

import fnc

from .helpers import AttrObject, IterMappingObject, KeysGetItemObject


parametrize = pytest.mark.parametrize


@parametrize(
    "case",
    [
        dict(args=([0, 2, 4], ["a", "b", "c", "d", "e"]), expected=("a", "c", "e")),
        dict(args=([0, 2], ["moe", "larry", "curly"]), expected=("moe", "curly")),
        dict(args=(["a", "b"], {"a": 1, "b": 2, "c": 3}), expected=(1, 2)),
    ],
)
def test_at(case):
    assert fnc.at(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=({"name": "barney"}, {"name": "fred", "employer": "slate"}),
            expected={"name": "barney", "employer": "slate"},
        )
    ],
)
def test_defaults(case):
    assert fnc.defaults(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=("one.two", {"one": {"two": {"three": 4}}}), expected={"three": 4}),
        dict(args=("one.two.three", {"one": {"two": {"three": 4}}}), expected=4),
        dict(args=(["one", "two"], {"one": {"two": {"three": 4}}}), expected={"three": 4}),
        dict(args=(["one", "two", "three"], {"one": {"two": {"three": 4}}}), expected=4),
        dict(args=("one.four", {"one": {"two": {"three": 4}}}), expected=None),
        dict(
            args=("one.four.three", {"one": {"two": {"three": 4}}}),
            kwargs={"default": []},
            expected=[],
        ),
        dict(
            args=("one.four.0.a", {"one": {"two": {"three": 4}}}),
            kwargs={"default": [{"a": 1}]},
            expected=[{"a": 1}],
        ),
        dict(
            args=("one.four.three.0.a", {"one": {"two": {"three": [{"a": 1}]}}}),
            kwargs={"default": []},
            expected=[],
        ),
        dict(args=("one.four.three", {"one": {"two": {"three": 4}}}), expected=None),
        dict(
            args=("one.four.three.0.a", {"one": {"two": {"three": [{"a": 1}]}}}),
            expected=None,
        ),
        dict(
            args=("one.four.three", {"one": {"two": {"three": 4}}}),
            kwargs={"default": 2},
            expected=2,
        ),
        dict(
            args=("one.four.three.0.a", {"one": {"two": {"three": [{"a": 1}]}}}),
            kwargs={"default": 2},
            expected=2,
        ),
        dict(
            args=("one.four.three", {"one": {"two": {"three": 4}}}),
            kwargs={"default": {"test": "value"}},
            expected={"test": "value"},
        ),
        dict(
            args=("one.four.three.0.a", {"one": {"two": {"three": [{"a": 1}]}}}),
            kwargs={"default": {"test": "value"}},
            expected={"test": "value"},
        ),
        dict(
            args=("one.four.three", {"one": {"two": {"three": 4}}}),
            kwargs={"default": "haha"},
            expected="haha",
        ),
        dict(
            args=("one.four.three.0.a", {"one": {"two": {"three": [{"a": 1}]}}}),
            kwargs={"default": "haha"},
            expected="haha",
        ),
        dict(args=("five", {"one": {"two": {"three": 4}}}), expected=None),
        dict(
            args=(["one", 1, "three", 1], {"one": ["two", {"three": [4, 5]}]}),
            expected=5,
        ),
        dict(args=("one.[1].three.[1]", {"one": ["two", {"three": [4, 5]}]}), expected=5),
        dict(args=("one.1.three.1", {"one": ["two", {"three": [4, 5]}]}), expected=5),
        dict(args=("[1].two.three.[0]", ["one", {"two": {"three": [4, 5]}}]), expected=4),
        dict(
            args=(
                "[1].two.three[1][0].four[0]",
                ["one", {"two": {"three": [4, [{"four": [5]}]]}}],
            ),
            expected=5,
        ),
        dict(args=("[42]", range(50)), expected=42),
        dict(args=("[0][0][0][0][0][0][0][0][0][0]", [[[[[[[[[[42]]]]]]]]]]), expected=42),
        dict(args=("[0][42]", [range(50)]), expected=42),
        dict(args=("a[0].b[42]", {"a": [{"b": range(50)}]}), expected=42),
        dict(
            args=("one.bad.hello", {"one": ["hello", "there"]}),
            kwargs={"default": []},
            expected=[],
        ),
        dict(args=("one.1.hello", {"one": ["hello", None]}), expected=None),
        dict(args=("a", namedtuple("a", ["a", "b"])(1, 2)), expected=1),
        dict(args=(0, namedtuple("a", ["a", "b"])(1, 2)), expected=1),
        dict(args=("a.c.d", namedtuple("a", ["a", "b"])({"c": {"d": 1}}, 2)), expected=1),
        dict(args=("update", {}), expected=None),
        dict(args=("extend", []), expected=None),
        dict(args=((1,), {(1,): {(2,): 3}}), expected={(2,): 3}),
        dict(args=([(1,)], {(1,): {(2,): 3}}), expected={(2,): 3}),
        dict(args=([(1,), (2,)], {(1,): {(2,): 3}}), expected=3),
        dict(args=(object, {object: 1}), expected=1),
        dict(args=([object, object], {object: {object: 1}}), expected=1),
        dict(args=("0.0.0.0.0.0.0.0.0.0", [[[[[[[[[[42]]]]]]]]]]), expected=42),
        dict(args=("1.name", {1: {"name": "John Doe"}}), expected="John Doe"),
    ],
)
def test_get(case):
    kwargs = case.get("kwargs", {})
    assert fnc.get(*case["args"], **kwargs) == case["expected"]


def test_get__should_not_populate_defaultdict():
    data = defaultdict(list)
    fnc.get("a", data)
    assert data == {}


@parametrize(
    "case",
    [
        dict(args=("b", {"a": 1, "b": 2, "c": 3}), expected=True),
        dict(args=(0, [1, 2, 3]), expected=True),
        dict(args=(1, [1, 2, 3]), expected=True),
        dict(args=(3, [1, 2, 3]), expected=False),
        dict(args=("b", {"a": 1, "b": 2, "c": 3}), expected=True),
        dict(args=(0, [1, 2, 3]), expected=True),
        dict(args=(1, [1, 2, 3]), expected=True),
        dict(args=(3, [1, 2, 3]), expected=False),
        dict(args=("one.two", {"one": {"two": {"three": 4}}}), expected=True),
        dict(args=("one.two.three", {"one": {"two": {"three": 4}}}), expected=True),
        dict(args=(["one", "two"], {"one": {"two": {"three": 4}}}), expected=True),
        dict(
            args=(["one", "two", "three"], {"one": {"two": {"three": 4}}}),
            expected=True,
        ),
        dict(args=("one.four", {"one": {"two": {"three": 4}}}), expected=False),
        dict(args=("five", {"one": {"two": {"three": 4}}}), expected=False),
        dict(args=("one.four.three", {"one": {"two": {"three": 4}}}), expected=False),
        dict(
            args=("one.four.three.0.a", {"one": {"two": {"three": [{"a": 1}]}}}),
            expected=False,
        ),
        dict(
            args=(["one", 1, "three", 1], {"one": ["two", {"three": [4, 5]}]}),
            expected=True,
        ),
        dict(
            args=("one.[1].three.[1]", {"one": ["two", {"three": [4, 5]}]}),
            expected=True,
        ),
        dict(args=("one.1.three.1", {"one": ["two", {"three": [4, 5]}]}), expected=True),
        dict(
            args=("[1].two.three.[0]", ["one", {"two": {"three": [4, 5]}}]),
            expected=True,
        ),
    ],
)
def test_has(case):
    assert fnc.has(*case["args"]) == case["expected"]


def test_has__should_not_populate_defaultdict():
    data = defaultdict(list)
    fnc.has("a", data)
    assert data == {}


@parametrize(
    "case",
    [
        dict(args=({"a": 1, "b": 2, "c": 3},), expected={1: "a", 2: "b", 3: "c"}),
        dict(
            args=(IterMappingObject({"a": 1, "b": 2, "c": 3}),),
            expected={1: "a", 2: "b", 3: "c"},
        ),
        dict(args=([1, 2, 3],), expected={1: 0, 2: 1, 3: 2}),
    ],
)
def test_invert(case):
    assert fnc.invert(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(lambda k: k + k, {0: "a", 1: "b", 2: "c"}),
            expected={0: "a", 2: "b", 4: "c"},
        ),
        dict(
            args=(lambda k: k + k, KeysGetItemObject({0: "a", 1: "b", 2: "c"})),
            expected={0: "a", 2: "b", 4: "c"},
        ),
    ],
)
def test_mapkeys(case):
    assert fnc.mapkeys(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(lambda num: num * 3, {"a": 1, "b": 2, "c": 3}),
            expected={"a": 3, "b": 6, "c": 9},
        ),
        dict(
            args=(
                "age",
                {
                    "fred": {"name": "fred", "age": 40},
                    "pebbles": {"name": "pebbles", "age": 1},
                },
            ),
            expected={"fred": 40, "pebbles": 1},
        ),
    ],
)
def test_mapvalues(case):
    assert fnc.mapvalues(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=({"name": "fred"}, {"company": "a"}),
            expected={"name": "fred", "company": "a"},
        ),
        dict(
            args=({"name": "fred"}, {"company": "a"}, {"company": "b"}),
            expected={"name": "fred", "company": "b"},
        ),
    ],
)
def test_merge(case):
    assert fnc.merge(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(["a"], {"a": 1, "b": 2, "c": 3}), expected={"b": 2, "c": 3}),
        dict(args=(["a", "b"], {"a": 1, "b": 2, "c": 3}), expected={"c": 3}),
        dict(args=([], [1, 2, 3]), expected={0: 1, 1: 2, 2: 3}),
        dict(args=([0], [1, 2, 3]), expected={1: 2, 2: 3}),
        dict(args=([0, 1], [1, 2, 3]), expected={2: 3}),
    ],
)
def test_omit(case):
    assert fnc.omit(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(["a"], {"a": 1, "b": 2, "c": 3}), expected={"a": 1}),
        dict(args=(["a", "b"], {"a": 1, "b": 2, "c": 3}), expected={"a": 1, "b": 2}),
        dict(args=(["a"], {}), expected={}),
        dict(args=([], [1, 2, 3]), expected={}),
        dict(args=([0], [1, 2, 3]), expected={0: 1}),
        dict(args=(["a"], AttrObject(a=1, b=2, c=3)), expected={"a": 1}),
    ],
)
def test_pick(case):
    assert fnc.pick(*case["args"]) == case["expected"]
