import math

import pytest

import fnc


parametrize = pytest.mark.parametrize


@parametrize(
    "case",
    [
        dict(args=(1, [1, 2, 3, 4, 5]), expected=[[1], [2], [3], [4], [5]]),
        dict(args=(2, [1, 2, 3, 4, 5]), expected=[[1, 2], [3, 4], [5]]),
        dict(args=(3, [1, 2, 3, 4, 5]), expected=[[1, 2, 3], [4, 5]]),
        dict(args=(4, [1, 2, 3, 4, 5]), expected=[[1, 2, 3, 4], [5]]),
        dict(args=(5, [1, 2, 3, 4, 5]), expected=[[1, 2, 3, 4, 5]]),
        dict(args=(6, [1, 2, 3, 4, 5]), expected=[[1, 2, 3, 4, 5]]),
    ],
)
def test_chunk(case):
    assert list(fnc.chunk(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=([0, 1, 2, 3],), expected=[1, 2, 3]),
        dict(args=([True, False, None, True, 1, "foo"],), expected=[True, True, 1, "foo"]),
    ],
)
def test_compact(case):
    assert list(fnc.compact(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(), expected=[]),
        dict(args=([],), expected=[]),
        dict(args=([1, 2, 3],), expected=[1, 2, 3]),
        dict(args=([1, 2, 3], [4, 5, 6]), expected=[1, 2, 3, 4, 5, 6]),
        dict(args=([1, 2, 3], [4, 5, 6], [7]), expected=[1, 2, 3, 4, 5, 6, 7]),
        dict(args=([1], [2], [3], [4]), expected=[1, 2, 3, 4]),
    ],
)
def test_concat(case):
    assert list(fnc.concat(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(lambda num: int(math.floor(num)), [4.3, 6.1, 6.4]),
            expected={4: 1, 6: 2},
        ),
        dict(
            args=({"one": 1}, [{"one": 1}, {"one": 1}, {"two": 2}, {"one": 1}]),
            expected={True: 3, False: 1},
        ),
        dict(
            args=("one", [{"one": 1}, {"one": 1}, {"two": 2}, {"one": 1}]),
            expected={1: 3, None: 1},
        ),
        dict(args=(None, {1: 0, 2: 0, 4: 3}), expected={1: 1, 2: 1, 4: 1}),
    ],
)
def test_countby(case):
    assert fnc.countby(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=([1, 2, 3, 4],), expected=[1, 2, 3, 4]),
        dict(args=([1, 2, 3, 4], []), expected=[1, 2, 3, 4]),
        dict(args=([1, 2, 3, 4], [2, 4], [3, 5, 6]), expected=[1]),
        dict(args=([1, 1, 1, 1], [2, 4], [3, 5, 6]), expected=[1]),
        dict(args=(iter([1, 2, 3, 4]), iter([2, 4]), iter([1, 3, 5, 6])), expected=[]),
        dict(args=(iter([0, 1, 2, 3, 4]), iter([2, 4]), iter([1, 3, 5, 6])), expected=[0]),
    ],
)
def test_difference(case):
    assert list(fnc.difference(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=("a", [{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}]),
            expected=[{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}],
        ),
        dict(
            args=(round, [1.5, 2.2, 3.7, 4.2], [2.5, 4.9], [3, 5, 6]),
            expected=[3.7],
        ),
    ],
)
def test_differenceby(case):
    assert list(fnc.differenceby(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=([1, 2, 3, 2, 1, 5, 6, 5, 5, 5],), expected=[2, 1, 5]),
        dict(args=([1, 2], [3, 2], [1, 5], [6, 5, 5, 5]), expected=[2, 1, 5]),
        dict(args=([1, 2], [3, 2], [1, 5], [6, 5, 5, 5]), expected=[2, 1, 5]),
        dict(
            args=(iter([1, 2]), iter([3, 2]), iter([1, 5]), iter([6, 5, 5, 5])),
            expected=[2, 1, 5],
        ),
    ],
)
def test_duplicates(case):
    assert list(fnc.duplicates(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(
                "a",
                [
                    {"a": 1},
                    {"a": 2},
                    {"a": 3},
                    {"a": 2},
                    {"a": 1},
                    {"a": 5},
                    {"a": 6},
                    {"a": 5},
                    {"a": 5},
                    {"a": 5},
                ],
            ),
            expected=[{"a": 2}, {"a": 1}, {"a": 5}],
        ),
        dict(
            args=(
                lambda x: round(x),
                [1.5, 2.3],
                [3.7, 2.5],
                [1.1, 5.8],
                [6.9, 5.1, 5.2, 5.3],
            ),
            expected=[2.3, 5.2],
        ),
    ],
)
def test_duplicatesby(case):
    assert list(fnc.duplicatesby(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(None, [0, True, False, None, 1, 2, 3]), expected=[True, 1, 2, 3]),
        dict(args=(lambda num: num % 2 == 0, [1, 2, 3, 4, 5, 6]), expected=[2, 4, 6]),
        dict(
            args=(
                "blocked",
                [
                    {"name": "barney", "age": 36, "blocked": False},
                    {"name": "fred", "age": 40, "blocked": True},
                ],
            ),
            expected=[{"name": "fred", "age": 40, "blocked": True}],
        ),
        dict(
            args=(
                {"age": 36},
                [
                    {"name": "barney", "age": 36, "blocked": False},
                    {"name": "fred", "age": 40, "blocked": True},
                ],
            ),
            expected=[{"name": "barney", "age": 36, "blocked": False}],
        ),
        dict(
            args=(
                {"age": 40},
                [{"name": "moe", "age": 40}, {"name": "larry", "age": 50}],
            ),
            expected=[{"name": "moe", "age": 40}],
        ),
    ],
)
def test_filter(case):
    assert list(fnc.filter(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(
                lambda c: c["age"] < 40,
                [
                    {"name": "barney", "age": 36, "blocked": False},
                    {"name": "fred", "age": 40, "blocked": True},
                    {"name": "pebbles", "age": 1, "blocked": False},
                ],
            ),
            expected={"name": "barney", "age": 36, "blocked": False},
        ),
        dict(
            args=(
                {"age": 1},
                [
                    {"name": "barney", "age": 36, "blocked": False},
                    {"name": "fred", "age": 40, "blocked": True},
                    {"name": "pebbles", "age": 1, "blocked": False},
                ],
            ),
            expected={"name": "pebbles", "age": 1, "blocked": False},
        ),
        dict(
            args=(
                "blocked",
                [
                    {"name": "barney", "age": 36, "blocked": False},
                    {"name": "fred", "age": 40, "blocked": True},
                    {"name": "pebbles", "age": 1, "blocked": False},
                ],
            ),
            expected={"name": "fred", "age": 40, "blocked": True},
        ),
        dict(
            args=(
                None,
                [
                    {"name": "barney", "age": 36, "blocked": False},
                    {"name": "fred", "age": 40, "blocked": True},
                    {"name": "pebbles", "age": 1, "blocked": False},
                ],
            ),
            expected={"name": "barney", "age": 36, "blocked": False},
        ),
    ],
)
def test_find(case):
    assert fnc.find(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(lambda item: item.startswith("b"), ["apple", "banana", "beet"]),
            expected=1,
        ),
        dict(
            args=(
                {"name": "banana"},
                [
                    {"name": "apple", "type": "fruit"},
                    {"name": "banana", "type": "fruit"},
                    {"name": "beet", "type": "vegetable"},
                ],
            ),
            expected=1,
        ),
        dict(args=(lambda *_: False, ["apple", "banana", "beet"]), expected=-1),
    ],
)
def test_findindex(case):
    assert fnc.findindex(*case["args"]) == case["expected"]


@parametrize("case", [dict(args=(lambda num: num % 2 == 1, [1, 2, 3, 4]), expected=3)])
def test_findlast(case):
    assert fnc.findlast(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(lambda item: item.startswith("b"), ["apple", "banana", "beet"]),
            expected=2,
        ),
        dict(
            args=(
                {"type": "fruit"},
                [
                    {"name": "apple", "type": "fruit"},
                    {"name": "banana", "type": "fruit"},
                    {"name": "beet", "type": "vegetable"},
                ],
            ),
            expected=1,
        ),
        dict(args=(lambda *_: False, ["apple", "banana", "beet"]), expected=-1),
    ],
)
def test_findlastindex(case):
    assert fnc.findlastindex(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=([1, ["2222"], [3, [[4]]]], [[[[5]]]]),
            expected=[1, "2222", 3, [[4]], [[5]]],
        )
    ],
)
def test_flatten(case):
    assert list(fnc.flatten(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [dict(args=([1, ["2222"], [3, [[4]]]], [[[[5]]]]), expected=[1, "2222", 3, 4, 5])],
)
def test_flattendeep(case):
    assert list(fnc.flattendeep(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(
                ["a"],
                [
                    {"a": 1, "b": 2, "c": 3},
                    {"a": 1, "b": 2, "c": 4},
                    {"a": 1, "b": 2, "c": 5},
                    {"a": 1, "b": 1, "c": 6},
                    {"a": 1, "b": 1, "c": 7},
                    {"a": 2, "b": 2, "c": 8},
                    {"a": 2, "b": 2, "c": 9},
                    {"a": 2, "b": 2, "c": 10},
                    {"a": 3, "b": 1, "c": 11},
                ],
            ),
            expected={
                1: [
                    {"a": 1, "b": 2, "c": 3},
                    {"a": 1, "b": 2, "c": 4},
                    {"a": 1, "b": 2, "c": 5},
                    {"a": 1, "b": 1, "c": 6},
                    {"a": 1, "b": 1, "c": 7},
                ],
                2: [
                    {"a": 2, "b": 2, "c": 8},
                    {"a": 2, "b": 2, "c": 9},
                    {"a": 2, "b": 2, "c": 10},
                ],
                3: [{"a": 3, "b": 1, "c": 11}],
            },
        ),
        dict(
            args=(
                ["a", "b"],
                [
                    {"a": 1, "b": 2, "c": 3},
                    {"a": 1, "b": 2, "c": 4},
                    {"a": 1, "b": 2, "c": 5},
                    {"a": 1, "b": 1, "c": 6},
                    {"a": 1, "b": 1, "c": 7},
                    {"a": 2, "b": 2, "c": 8},
                    {"a": 2, "b": 2, "c": 9},
                    {"a": 2, "b": 2, "c": 10},
                    {"a": 3, "b": 1, "c": 11},
                ],
            ),
            expected={
                1: {
                    2: [
                        {"a": 1, "b": 2, "c": 3},
                        {"a": 1, "b": 2, "c": 4},
                        {"a": 1, "b": 2, "c": 5},
                    ],
                    1: [{"a": 1, "b": 1, "c": 6}, {"a": 1, "b": 1, "c": 7}],
                },
                2: {
                    2: [
                        {"a": 2, "b": 2, "c": 8},
                        {"a": 2, "b": 2, "c": 9},
                        {"a": 2, "b": 2, "c": 10},
                    ]
                },
                3: {1: [{"a": 3, "b": 1, "c": 11}]},
            },
        ),
        dict(
            args=(
                [],
                [
                    {"a": 1, "b": 2, "c": 3},
                    {"a": 1, "b": 2, "c": 4},
                    {"a": 1, "b": 2, "c": 5},
                    {"a": 1, "b": 1, "c": 6},
                    {"a": 1, "b": 1, "c": 7},
                    {"a": 2, "b": 2, "c": 8},
                    {"a": 2, "b": 2, "c": 9},
                    {"a": 2, "b": 2, "c": 10},
                    {"a": 3, "b": 1, "c": 11},
                ],
            ),
            expected=[
                {"a": 1, "b": 2, "c": 3},
                {"a": 1, "b": 2, "c": 4},
                {"a": 1, "b": 2, "c": 5},
                {"a": 1, "b": 1, "c": 6},
                {"a": 1, "b": 1, "c": 7},
                {"a": 2, "b": 2, "c": 8},
                {"a": 2, "b": 2, "c": 9},
                {"a": 2, "b": 2, "c": 10},
                {"a": 3, "b": 1, "c": 11},
            ],
        ),
    ],
)
def test_groupall(case):
    assert fnc.groupall(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(lambda num: int(math.floor(num)), [4.2, 6.1, 6.4]),
            expected={4: [4.2], 6: [6.1, 6.4]},
        )
    ],
)
def test_groupby(case):
    assert fnc.groupby(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=([1, 2, 3], [[10, 20], [30, 40], [50, 60]]),
            expected=[10, 20, 1, 2, 3, 30, 40, 1, 2, 3, 50, 60],
        ),
        dict(
            args=([1, 2, 3], [[[10, 20]], [[30, 40]], [50, [60]]]),
            expected=[[10, 20], 1, 2, 3, [30, 40], 1, 2, 3, 50, [60]],
        ),
    ],
)
def test_intercalate(case):
    assert list(fnc.intercalate(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=([1, 2], [3, 4]), expected=[1, 3, 2, 4]),
        dict(args=([1, 2], [3, 4], [5, 6]), expected=[1, 3, 5, 2, 4, 6]),
        dict(args=([1, 2], [3, 4, 5], [6]), expected=[1, 3, 6, 2, 4, 5]),
        dict(args=([1, 2, 3], [4], [5, 6]), expected=[1, 4, 5, 2, 6, 3]),
    ],
)
def test_interleave(case):
    assert list(fnc.interleave(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=([1, 2, 3], [101, 2, 1, 10], [2, 1]), expected=[1, 2]),
        dict(args=([1, 1, 2, 2], [1, 1, 2, 2]), expected=[1, 2]),
        dict(args=([1, 2, 3], [4]), expected=[]),
        dict(args=([1, 2, 3],), expected=[1, 2, 3]),
        dict(args=([], [101, 2, 1, 10], [2, 1]), expected=[]),
        dict(args=([],), expected=[]),
        dict(args=[iter([2, 1]), iter([2, 1])], expected=[2, 1]),
        dict(args=[iter([2, 1]), iter([1, 2])], expected=[2, 1]),
        dict(args=[iter([2, 1]), iter([1, 2]), iter([0, 1, 2]), iter([1])], expected=[1]),
        dict(args=[iter([1, 2]), iter([2, 1]), iter([0, 1, 2]), iter([1])], expected=[1]),
    ],
)
def test_intersection(case):
    assert list(fnc.intersection(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(
                "a",
                [{"a": 1}, {"a": 2}, {"a": 3}],
                [{"a": 101}, {"a": 2}, {"a": 1}, {"a": 10}],
                [{"a": 2}, {"a": 1}],
            ),
            expected=[{"a": 1}, {"a": 2}],
        ),
        dict(
            args=(lambda x: round(x), [1.5, 1.7, 2.1, 2.8], [1, 1, 2, 2]),
            expected=[1.5],
        ),
    ],
)
def test_intersectionby(case):
    assert list(fnc.intersectionby(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(10, []), expected=[]),
        dict(args=(10, [1]), expected=[1]),
        dict(args=(10, [1, 2, 3, 4]), expected=[1, 10, 2, 10, 3, 10, 4]),
        dict(
            args=([0, 0, 0], [1, 2, 3, 4]),
            expected=[1, [0, 0, 0], 2, [0, 0, 0], 3, [0, 0, 0], 4],
        ),
        dict(
            args=([0, 0, 0], [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
            expected=[[1, 2, 3], [0, 0, 0], [4, 5, 6], [0, 0, 0], [7, 8, 9]],
        ),
    ],
)
def test_intersperse(case):
    assert list(fnc.intersperse(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=("dir", [{"dir": "left", "code": 97}, {"dir": "right", "code": 100}]),
            expected={
                "left": {"dir": "left", "code": 97},
                "right": {"dir": "right", "code": 100},
            },
        )
    ],
)
def test_keyby(case):
    assert fnc.keyby(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(None, [1, 2, 3]), expected=[1, 2, 3]),
        dict(args=(int, [1.1, 2.1, 3.1]), expected=[1, 2, 3]),
        dict(args=(lambda num: num * 3, [1, 2, 3]), expected=[3, 6, 9]),
        dict(args=(len, [[1], [2, 3], [4, 5, 6]]), expected=[1, 2, 3]),
        dict(
            args=("name", [{"name": "moe", "age": 40}, {"name": "larry", "age": 50}]),
            expected=["moe", "larry"],
        ),
        dict(
            args=(
                "level1.level2.level3.value",
                [
                    {"level1": {"level2": {"level3": {"value": 1}}}},
                    {"level1": {"level2": {"level3": {"value": 2}}}},
                    {"level1": {"level2": {"level3": {"value": 3}}}},
                    {"level1": {"level2": {"level3": {"value": 4}}}},
                    {"level1": {"level2": {}}},
                    {},
                ],
            ),
            expected=[1, 2, 3, 4, None, None],
        ),
        dict(args=([1], [[0, 1], [2, 3], [4, 5]]), expected=[1, 3, 5]),
        dict(
            args=(
                ["a"],
                [
                    {"a": 1, "b": 2, "c": -1},
                    {"a": 3, "b": 4, "c": -1},
                    {"a": 5, "b": 6, "c": -1},
                ],
            ),
            expected=[1, 3, 5],
        ),
        dict(
            args=(
                ("a", "b"),
                [
                    {"a": 1, "b": 2, "c": -1},
                    {"a": 3, "b": 4, "c": -1},
                    {"a": 5, "b": 6, "c": -1},
                ],
            ),
            expected=[(1, 2), (3, 4), (5, 6)],
        ),
        dict(
            args=(
                {"a", "b"},
                [
                    {"a": 1, "b": 2, "c": -1},
                    {"a": 3, "b": 4, "c": -1},
                    {"a": 5, "b": 6, "c": -1},
                ],
            ),
            expected=[{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 6}],
        ),
    ],
)
def test_map(case):
    assert list(fnc.map(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(lambda x: [str(x)] if x is None else [], [1, 2, None, 4, None, 6]),
            expected=["None", "None"],
        )
    ],
)
def test_mapcat(case):
    assert list(fnc.mapcat(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(None, [1, 2, 3]), expected=[1, 2, 3]),
        dict(args=(None, [[1], [2], [3]]), expected=[1, 2, 3]),
        dict(args=(None, [[[1]], [[2]], [[3]]]), expected=[[1], [2], [3]]),
        dict(args=(lambda x: [x - 1], [1, 2, 3]), expected=[0, 1, 2]),
        dict(
            args=(lambda x: [[x], [x]], [1, 2, 3]),
            expected=[[1], [1], [2], [2], [3], [3]],
        ),
    ],
)
def test_mapflat(case):
    assert list(fnc.mapflat(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(None, [1, 2, 3]), expected=[1, 2, 3]),
        dict(args=(None, [[1], [2], [3]]), expected=[1, 2, 3]),
        dict(args=(None, [[[1]], [[2]], [[3]]]), expected=[1, 2, 3]),
        dict(args=(lambda x: [x - 1], [1, 2, 3]), expected=[0, 1, 2]),
        dict(args=(lambda x: [[x], [x]], [1, 2, 3]), expected=[1, 1, 2, 2, 3, 3]),
    ],
)
def test_mapflatdeep(case):
    assert list(fnc.mapflatdeep(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(lambda item: item % 2, [1, 2, 3]), expected=[[1, 3], [2]]),
        dict(
            args=(lambda item: math.floor(item) % 2, [1.2, 2.3, 3.4]),
            expected=[[1.2, 3.4], [2.3]],
        ),
        dict(
            args=(
                {"age": 1},
                [
                    {"name": "barney", "age": 36},
                    {"name": "fred", "age": 40, "blocked": True},
                    {"name": "pebbles", "age": 1},
                ],
            ),
            expected=[
                [{"name": "pebbles", "age": 1}],
                [
                    {"name": "barney", "age": 36},
                    {"name": "fred", "age": 40, "blocked": True},
                ],
            ],
        ),
        dict(
            args=(
                "blocked",
                [
                    {"name": "barney", "age": 36},
                    {"name": "fred", "age": 40, "blocked": True},
                    {"name": "pebbles", "age": 1},
                ],
            ),
            expected=[
                [{"name": "fred", "age": 40, "blocked": True}],
                [{"name": "barney", "age": 36}, {"name": "pebbles", "age": 1}],
            ],
        ),
    ],
)
def test_partition(case):
    assert list(fnc.partition(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(None, [0, True, False, None, 1, 2, 3]), expected=[0, False, None]),
        dict(args=(lambda num: num % 2 == 0, [1, 2, 3, 4, 5, 6]), expected=[1, 3, 5]),
        dict(
            args=(
                "blocked",
                [
                    {"name": "barney", "age": 36, "blocked": False},
                    {"name": "fred", "age": 40, "blocked": True},
                ],
            ),
            expected=[{"name": "barney", "age": 36, "blocked": False}],
        ),
        dict(
            args=(
                {"age": 36},
                [
                    {"name": "barney", "age": 36, "blocked": False},
                    {"name": "fred", "age": 40, "blocked": True},
                ],
            ),
            expected=[{"name": "fred", "age": 40, "blocked": True}],
        ),
    ],
)
def test_reject(case):
    assert list(fnc.reject(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=([1, 2, 1, 3, 1], [1, 3, 2, 6, 4], [5]), expected=[1, 2, 3, 6, 4, 5]),
        dict(args=([dict(a=1), dict(a=2), dict(a=1)],), expected=[dict(a=1), dict(a=2)]),
    ],
)
def test_union(case):
    assert list(fnc.union(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=(
                "a",
                [dict(a=1), dict(a=2), dict(a=1), dict(a=3), dict(a=1)],
                [dict(a=1), dict(a=3), dict(a=2), dict(a=6), dict(a=4)],
                [dict(a=5)],
            ),
            expected=[dict(a=1), dict(a=2), dict(a=3), dict(a=6), dict(a=4), dict(a=5)],
        ),
        dict(
            args=(lambda x: round(x["a"]), [dict(a=1.7), dict(a=2), dict(a=1)]),
            expected=[dict(a=1.7), dict(a=1)],
        ),
    ],
)
def test_unionby(case):
    assert list(fnc.unionby(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(
            args=([["moe", 30, True], ["larry", 40, False], ["curly", 35, True]],),
            expected=[("moe", "larry", "curly"), (30, 40, 35), (True, False, True)],
        )
    ],
)
def test_unzip(case):
    assert list(fnc.unzip(*case["args"])) == case["expected"]


@parametrize("case", [dict(args=([0, 1], [1, 2, 1, 0, 3, 1, 4]), expected=[2, 3, 4])])
def test_without(case):
    assert list(fnc.without(*case["args"])) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=([1, 2, 3], [5, 2, 1, 4]), expected=[3, 5, 4]),
        dict(args=([1, 2, 5], [2, 3, 5], [3, 4, 5]), expected=[1, 4, 5]),
        dict(args=(iter([1, 2, 5]), iter([2, 3, 5]), iter([3, 4, 5])), expected=[1, 4, 5]),
        dict(
            args=(
                iter(x for x in [1, 2, 5]),
                iter(x for x in [2, 3, 5]),
                iter(x for x in [3, 4, 5]),
            ),
            expected=[1, 4, 5],
        ),
    ],
)
def test_xor(case):
    assert list(fnc.xor(*case["args"])) == case["expected"]
