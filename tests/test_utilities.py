from unittest import mock

import pytest

import fnc


parametrize = pytest.mark.parametrize


def test_after():
    tracker = []

    def track_one():
        tracker.append(1)

    @fnc.after(track_one)
    def track_two():
        tracker.append(2)
        return True

    assert track_two() is True
    assert tracker == [2, 1]


@parametrize(
    "case",
    [
        dict(args=("a.b.c",), expected=["a", "b", "c"]),
        dict(args=("a[0].b.c",), expected=["a", "0", "b", "c"]),
        dict(args=("a[0][1][2].b.c",), expected=["a", "0", "1", "2", "b", "c"]),
        dict(
            args=(["a", "0", "1", "2", "b", "c"],),
            expected=["a", "0", "1", "2", "b", "c"],
        ),
        dict(args=((1, 2),), expected=[(1, 2)]),
    ],
)
def test_aspath(case):
    assert fnc.aspath(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=([0, 2, 4], ["a", "b", "c", "d", "e"]), expected=("a", "c", "e")),
        dict(args=([0, 2], ["moe", "larry", "curly"]), expected=("moe", "curly")),
        dict(args=(["a", "b"], {"a": 1, "b": 2, "c": 3}), expected=(1, 2)),
    ],
)
def test_atgetter(case):
    assert fnc.atgetter(case["args"][0])(case["args"][1]) == case["expected"]


def test_before():
    tracker = []

    def track_one():
        tracker.append(1)

    @fnc.before(track_one)
    def track_two():
        tracker.append(2)
        return True

    assert track_two() is True
    assert tracker == [1, 2]


@parametrize(
    "case",
    [
        dict(
            funcs=(lambda x: "!!!" + x + "!!!", lambda x: f"Hi {x}"),
            args=("Bob",),
            expected="Hi !!!Bob!!!",
        ),
        dict(funcs=(lambda x: x + x, lambda x: x * x), args=(5,), expected=100),
        dict(
            funcs=((fnc.map, tuple), (fnc.map, list), tuple),
            args=([{"a": 1}, {"b": 2}, {"c": 3}],),
            expected=(["a"], ["b"], ["c"]),
        ),
        dict(
            funcs=((fnc.filter, lambda item: item[0][1] > 0), (fnc.map, dict), list),
            args=([[("a", 1)], [("a", 0)], [("a", 5)], [("a", -2)]],),
            expected=[{"a": 1}, {"a": 5}],
        ),
    ],
)
def test_compose(case):
    assert fnc.compose(*case["funcs"])(*case["args"]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=({"age": 40}, {"name": "fred", "age": 40}), expected=True),
        dict(
            args=({"age": 40, "active": True}, {"name": "fred", "age": 40}),
            expected=False,
        ),
        dict(args=({}, {}), expected=True),
        dict(args=({}, {"a": 1}), expected=True),
    ],
)
def test_conformance(case):
    expected = case["expected"]
    assert fnc.conformance(case["args"][0])(case["args"][1]) == expected


@parametrize(
    "case",
    [
        dict(args=({"age": 40}, {"name": "fred", "age": 40}), expected=True),
        dict(
            args=({"age": 40, "active": True}, {"name": "fred", "age": 40}),
            expected=False,
        ),
        dict(
            args=({"age": lambda age: age >= 21}, {"name": "fred", "age": 21}),
            expected=True,
        ),
        dict(
            args=({"age": lambda age: age >= 21}, {"name": "fred", "age": 19}),
            expected=False,
        ),
        dict(args=({}, {}), expected=True),
        dict(args=({}, {"a": 1}), expected=True),
    ],
)
def test_conforms(case):
    assert fnc.conforms(*case["args"]) == case["expected"]


@parametrize("case", ["foo", "bar", {"a": 1}])
def test_constant(case):
    assert fnc.constant(case)() is case


@parametrize(
    "case",
    [
        dict(args=(1,), expected=1),
        dict(args=(1, 2), expected=1),
        dict(args=(), expected=None),
        dict(args=(1, 2), kwargs={"a": 3, "b": 4}, expected=1),
    ],
)
def test_identity(case):
    kwargs = case.get("kwargs", {})
    assert fnc.identity(*case["args"], **kwargs) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(lambda a, b: a + b, 1, 2), expected=3),
        dict(args=(None, 1, 2), expected=1),
        dict(args=({"a": 1, "b": 2}, {"a": 1, "b": 2, "c": 3}), expected=True),
        dict(args=({"a": 1, "b": 2}, {"a": 4, "b": 2, "c": 3}), expected=False),
        dict(
            args=({"a", "b"}, {"a": 1, "b": 2, "c": 3, "d": 4}),
            expected={"a": 1, "b": 2},
        ),
        dict(args=(("a", "b"), {"a": 1, "b": 2, "c": 3, "d": 4}), expected=(1, 2)),
        dict(args=("a", {"a": 1, "b": 2}), expected=1),
        dict(args=("a.b", {"a": {"b": 2}}), expected=2),
        dict(args=(["a", "b"], {"a": {"b": 2}}), expected=2),
    ],
)
def test_iteratee(case):
    args = case["args"]
    assert fnc.iteratee(args[0])(*args[1:]) == case["expected"]


@parametrize(
    "case",
    [dict(args=(lambda item: item, True)), dict(args=(lambda item: item, False))],
)
def test_negate(case):
    func, *callargs = case["args"]
    assert fnc.negate(func)(*callargs) == (not func(*callargs))


@parametrize(
    "case",
    [
        dict(args=(), kwargs={}),
        dict(args=(1, 2, 3), kwargs={}),
        dict(args=(), kwargs={"a": 1, "b": 2}),
        dict(args=(1, 2, 3), kwargs={"a": 1, "b": 2}),
    ],
)
def test_noop(case):
    assert fnc.noop(*case["args"], **case["kwargs"]) is None


@parametrize("case", [dict(args=((max, min), [1, 2, 3, 4]), expected=(4, 1))])
def test_over(case):
    funcs, *callargs = case["args"]
    assert fnc.over(*funcs)(*callargs) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=((lambda x: x is not None, bool), 1), expected=True),
        dict(args=((lambda x: x is None, bool), 1), expected=False),
    ],
)
def test_overall(case):
    funcs, *callargs = case["args"]
    assert fnc.overall(*funcs)(*callargs) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=((lambda x: x is not None, bool), 1), expected=True),
        dict(args=((lambda x: x is None, bool), 1), expected=True),
        dict(args=((lambda x: x is False, lambda y: y == 2), True), expected=False),
    ],
)
def test_overany(case):
    funcs, *callargs = case["args"]
    assert fnc.overany(*funcs)(*callargs) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=("one.two", {"one": {"two": {"three": 4}}}), expected={"three": 4}),
        dict(
            args=("one.four.three", {"one": {"two": {"three": 4}}}),
            kwargs={"default": []},
            expected=[],
        ),
    ],
)
def test_pathgetter(case):
    args = case["args"]
    kwargs = case.get("kwargs", {})
    assert fnc.pathgetter(args[0], **kwargs)(args[1]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(["a"], {"a": 1, "b": 2, "c": 3}), expected={"a": 1}),
        dict(args=(["a", "b"], {"a": 1, "b": 2, "c": 3}), expected={"a": 1, "b": 2}),
        dict(args=([], [1, 2, 3]), expected={}),
        dict(args=([0], [1, 2, 3]), expected={0: 1}),
    ],
)
def test_pickgetter(case):
    assert fnc.pickgetter(case["args"][0])(case["args"][1]) == case["expected"]


@parametrize(
    "case",
    [
        dict(args=(), expected={"type": int, "min": 0, "max": 1}),
        dict(args=(25,), expected={"type": int, "min": 0, "max": 25}),
        dict(args=(5, 10), expected={"type": int, "min": 5, "max": 10}),
        dict(
            args=(),
            kwargs={"floating": True},
            expected={"type": float, "min": 0, "max": 1},
        ),
        dict(
            args=(25,),
            kwargs={"floating": True},
            expected={"type": float, "min": 0, "max": 25},
        ),
        dict(
            args=(5, 10),
            kwargs={"floating": True},
            expected={"type": float, "min": 5, "max": 10},
        ),
        dict(args=(5.0, 10), expected={"type": float, "min": 5, "max": 10}),
        dict(args=(5, 10.0), expected={"type": float, "min": 5, "max": 10}),
        dict(args=(5.0, 10.0), expected={"type": float, "min": 5, "max": 10}),
        dict(
            args=(5.0, 10.0),
            kwargs={"floating": True},
            expected={"type": float, "min": 5, "max": 10},
        ),
    ],
)
def test_random(case):
    kwargs = case.get("kwargs", {})

    for _ in range(50):
        rnd = fnc.random(*case["args"], **kwargs)
        assert isinstance(rnd, case["expected"]["type"])
        assert case["expected"]["min"] <= rnd <= case["expected"]["max"]


@parametrize(
    "case",
    [
        dict(args={"attempts": 3}, expected={"count": 0}),
        dict(args={"attempts": 3}, expected={"count": 1}),
        dict(args={"attempts": 3}, expected={"count": 2}),
        dict(args={"attempts": 5}, expected={"count": 3}),
    ],
)
def test_retry_success(mocksleep, case):
    counter = {True: 0}

    @fnc.retry(**case["args"])
    def func():
        if counter[True] != case["expected"]["count"]:
            counter[True] += 1
            raise Exception()
        return True

    result = func()

    assert result is True
    assert counter[True] == case["expected"]["count"]
    assert mocksleep.call_count == case["expected"]["count"]


@parametrize(
    "case",
    [
        dict(args={}, expected={"count": 2, "times": [0.5, 1.0]}),
        dict(args={"attempts": 1}, expected={"count": 0, "times": []}),
        dict(
            args={"attempts": 3, "delay": 0.5, "scale": 2.0},
            expected={"count": 2, "times": [0.5, 1.0]},
        ),
        dict(
            args={"attempts": 5, "delay": 1.5, "scale": 2.5},
            expected={"count": 4, "times": [1.5, 3.75, 9.375, 23.4375]},
        ),
        dict(
            args={"attempts": 5, "delay": 1.5, "max_delay": 8.0, "scale": 2.5},
            expected={"count": 4, "times": [1.5, 3.75, 8.0, 8.0]},
        ),
    ],
)
def test_retry_error(mocksleep, case):
    @fnc.retry(**case["args"])
    def func():
        raise Exception()

    with pytest.raises(Exception):
        func()

    assert mocksleep.call_count == case["expected"]["count"]

    delay_calls = [mock.call(time) for time in case["expected"]["times"]]
    assert mocksleep.call_args_list == delay_calls


@parametrize(
    "case",
    [
        dict(
            args={"jitter": 5, "delay": 2, "scale": 1, "attempts": 5},
            unexpected=[2, 2, 2, 2],
        ),
        dict(
            args={"jitter": 10, "delay": 3, "scale": 1.5, "attempts": 5},
            unexpected=[3, 4.5, 6.75, 10.125],
        ),
        dict(
            args={"jitter": 1.0, "delay": 3, "scale": 1.5, "attempts": 5},
            unexpected=[3, 4.5, 6.75, 10.125],
        ),
    ],
)
def test_retry_jitter(mocksleep, case):
    @fnc.retry(**case["args"])
    def func():
        raise Exception()

    with pytest.raises(Exception):
        func()

    delay_calls = [mock.call(time) for time in case["unexpected"]]

    assert mocksleep.call_count == len(delay_calls)
    assert mocksleep.call_args_list != delay_calls


@parametrize(
    "case",
    [
        dict(
            args={"attempts": 1, "exceptions": (RuntimeError,)},
            expected={"exception": RuntimeError, "count": 0},
        ),
        dict(
            args={"attempts": 2, "exceptions": (RuntimeError,)},
            expected={"exception": RuntimeError, "count": 1},
        ),
        dict(
            args={"attempts": 2, "exceptions": (RuntimeError,)},
            expected={"exception": Exception, "count": 0},
        ),
    ],
)
def test_retry_exceptions(mocksleep, case):
    @fnc.retry(**case["args"])
    def func():
        raise case["expected"]["exception"]()

    with pytest.raises(case["expected"]["exception"]):
        func()

    assert case["expected"]["count"] == mocksleep.call_count


def test_retry_on_exception(mocksleep):
    attempts = 5
    error_counts = {}

    def on_exception(exc):
        error_counts[exc.retry["attempt"]] = True

    @fnc.retry(attempts=attempts, on_exception=on_exception)
    def func():
        raise Exception()

    with pytest.raises(Exception):
        func()

    assert error_counts == {key: True for key in range(1, attempts + 1)}


@parametrize(
    "case",
    [
        dict(args={"attempts": 0}, exception=ValueError),
        dict(args={"attempts": "1"}, exception=ValueError),
        dict(args={"delay": -1}, exception=ValueError),
        dict(args={"delay": "1"}, exception=ValueError),
        dict(args={"max_delay": -1}, exception=ValueError),
        dict(args={"max_delay": "1"}, exception=ValueError),
        dict(args={"scale": 0}, exception=ValueError),
        dict(args={"scale": "1"}, exception=ValueError),
        dict(args={"jitter": -1}, exception=ValueError),
        dict(args={"jitter": "1"}, exception=ValueError),
        dict(args={"jitter": (1,)}, exception=ValueError),
        dict(args={"jitter": ("1", "2")}, exception=ValueError),
        dict(args={"exceptions": (1, 2)}, exception=TypeError),
        dict(args={"exceptions": 1}, exception=TypeError),
        dict(args={"exceptions": (Exception, 2)}, exception=TypeError),
        dict(args={"on_exception": 5}, exception=TypeError),
    ],
)
def test_retry_invalid_args(case):
    with pytest.raises(case["exception"]):
        fnc.retry(**case["args"])
