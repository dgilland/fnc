"""General utility functions."""

from collections.abc import Iterable
from functools import partial, wraps
from random import randint, uniform
import re
import time

import fnc

from .helpers import Sentinel, number_types


# These regexes are used in aspath() to parse deep path strings.

# This is used to split a deep path string into dict keys or list indexex.
# This matches "." as delimiter and "[<key>]" as delimiter while keeping the
# "[<key>]" as an item.
RE_PATH_KEY_DELIM = re.compile(r"(?<!\\)\.|(\[.*?\])")

# Matches on path strings like "[<key>]".
RE_PATH_GET_ITEM = re.compile(r"^\[.*?\]$")


def after(method):
    """
    Decorator that calls `method` after the decorated function is called.

    Examples:
        >>> def a(): print('a')
        >>> def b(): print('b')
        >>> after(a)(b)()
        b
        a

    Args:
        method (callable): Function to call afterwards.
    """

    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            method()
            return result

        return decorated

    return decorator


def aspath(value):
    """
    Converts value to an object path list.

    Examples:
        >>> aspath('a.b.c')
        ['a', 'b', 'c']
        >>> aspath('a.0.0.b.c')
        ['a', '0', '0', 'b', 'c']
        >>> aspath('a[0].b.c')
        ['a', '0', 'b', 'c']
        >>> aspath('a[0][1][2].b.c')
        ['a', '0', '1', '2', 'b', 'c']
        >>> aspath('[a][0][1][2][b][c]')
        ['a', '0', '1', '2', 'b', 'c']
        >>> aspath('a.[]')
        ['a', '']
        >>> aspath(0)
        [0]
        >>> aspath([0, 1])
        [0, 1]
        >>> aspath((0, 1))
        [(0, 1)]

    Args:
        value (object): Value to convert.

    Returns:
        list: Returns property paths.
    """
    if isinstance(value, list):
        return value

    if not isinstance(value, str):
        return [value]

    return [_parse_path_token(token) for token in RE_PATH_KEY_DELIM.split(value) if token]


def _parse_path_token(token):
    if RE_PATH_GET_ITEM.match(token):
        path = token[1:-1]
    else:
        path = token

    return path


def atgetter(paths):
    """
    Creates a function that returns the values at paths of a given object.

    Examples:
        >>> get_id_name = atgetter(['data.id', 'data.name'])
        >>> get_id_name({'data': {'id': 1, 'name': 'foo'}})
        (1, 'foo')

    Args:
        paths (Iterable): Path values to fetch from object.

    Returns:
        callable: Function like ``f(obj): fnc.at(paths, obj)``.
    """
    return partial(fnc.at, paths)


def before(method):
    """
    Decorator that calls `method` before the decorated function is called.

    Examples:
        >>> def a(): print('a')
        >>> def b(): print('b')
        >>> before(a)(b)()
        a
        b

    Args:
        method (callable): Function to call afterwards.
    """

    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            method()
            return func(*args, **kwargs)

        return decorated

    return decorator


def compose(*funcs):
    """
    Create a function that is the composition of the provided functions, where each successive
    invocation is supplied the return value of the previous. For example, composing the functions
    ``f()``, ``g()``, and ``h()`` produces ``h(g(f()))``.

    Note:
        Each element in `funcs` can either be a callable or a ``tuple`` where the first
        element is a callable and the remaining elements are partial arguments. The
        tuples will be converted to a callable using ``functools.partial(*func)``.

    Note:
        The "partial" shorthand only supports invoking ``functools.partial`` using
        positional arguments. If keywoard argument partials are needed, then use
        ``functools.partial`` directly.

    Examples:
        >>> mult_5 = lambda x: x * 5
        >>> div_10 = lambda x: x / 10.0
        >>> pow_2 = lambda x: x ** 2
        >>> mult_div_pow = compose(sum, mult_5, div_10, pow_2)
        >>> mult_div_pow([1, 2, 3, 4])
        25.0
        >>> sum_positive_evens = compose(
        ...     (filter, lambda x: x > 0),
        ...     (filter, lambda x: x % 2 == 0),
        ...     sum
        ... )
        >>> sum_positive_evens([-1, 1, 2, 3, -5, 0, 6])
        8

    Args:
        *funcs (callable): Function(s) to compose. If `func` is a tuple, then it will be
            converted into a partial using ``functools.partial(*func)``.

    Returns:
        callable: Composed function.
    """
    funcs = tuple(partial(*func) if isinstance(func, tuple) else func for func in funcs)

    def _compose(*args, **kwargs):
        result = None
        for func in funcs:
            result = func(*args, **kwargs)
            args, kwargs = (result,), {}
        return result

    return _compose


def conformance(source):
    """
    Creates a function that does a shallow comparison between a given object and the `source`
    dictionary using :func:`conforms`.

    Examples:
        >>> conformance({'a': 1})({'b': 2, 'a': 1})
        True
        >>> conformance({'a': 1})({'b': 2, 'a': 2})
        False

    Args:
        source (dict): Source object used for comparision.

    Returns:
        function
    """
    if not isinstance(source, dict):  # pragma: no cover
        raise TypeError("source must be a dict")

    return partial(conforms, source)


def conforms(source, target):
    """
    Return whether the `target` object conforms to `source` where `source` is a dictionary that
    contains key-value pairs which are compared against the same key- values in `target`. If a key-
    value in `source` is a callable, then that callable is used as a predicate against the
    corresponding key-value in `target`.

    Examples:
        >>> conforms({'b': 2}, {'a': 1, 'b': 2})
        True
        >>> conforms({'b': 3}, {'a': 1, 'b': 2})
        False
        >>> conforms({'b': 2, 'a': lambda a: a > 0}, {'a': 1, 'b': 2})
        True
        >>> conforms({'b': 2, 'a': lambda a: a > 0}, {'a': -1, 'b': 2})
        False

    Args:
        source (Mapping): Object of path values to match.
        target (Mapping): Object to compare.

    Returns:
        bool: Whether `target` is a match or not.
    """
    result = True
    for key, value in source.items():
        target_value = fnc.get(key, target, default=Sentinel)

        if target_value is Sentinel:
            target_result = False
        elif callable(value):
            target_result = value(target_value)
        else:
            target_result = target_value == value

        if not target_result:
            result = False
            break

    return result


def constant(value):
    """
    Creates a function that returns a constant `value`.

    Examples:
        >>> pi = constant(3.14)
        >>> pi()
        3.14

    Args:
        value (object): Constant value to return.

    Returns:
        callable: Function that always returns `value`.
    """
    return lambda *args, **kwargs: value


def identity(value=None, *args, **kwargs):
    """
    Return the first argument provided.

    Examples:
        >>> identity(1)
        1
        >>> identity(1, 2, 3)
        1
        >>> identity(1, 2, 3, a=4)
        1
        >>> identity() is None
        True

    Args:
        value (object, optional): Value to return. Defaults to ``None``.

    Returns:
        object: First argument or ``None``.
    """
    return value


def iteratee(obj):
    """
    Return iteratee function based on the type of `obj`.

    The iteratee object can be one of the following:

    - ``callable``: Return as-is.
    - ``None``: Return :func:`identity` function.
    - ``dict``: Return :func:`conformance(obj)` function.
    - ``set``: Return :func:`pickgetter(obj)` function.
    - ``tuple``: Return :func:`atgetter(obj)`` function.
    - otherwise: Return :func:`pathgetter(obj)`` function.

    Note:
        In most cases, this function won't need to be called directly since
        other functions that accept an iteratee will call this function
        internally.

    Examples:
        >>> iteratee(lambda a, b: a + b)(1, 2)
        3
        >>> iteratee(None)(1, 2, 3)
        1
        >>> is_active = iteratee({'active': True})
        >>> is_active({'active': True})
        True
        >>> is_active({'active': 0})
        False
        >>> iteratee({'a': 5, 'b.c': 1})({'a': 5, 'b': {'c': 1}})
        True
        >>> iteratee({'a', 'b'})({'a': 1, 'b': 2, 'c': 3}) == {'a': 1, 'b': 2}
        True
        >>> iteratee(('a', ['c', 'd', 'e']))({'a': 1, 'c': {'d': {'e': 3}}})
        (1, 3)
        >>> iteratee(['c', 'd', 'e'])({'a': 1, 'c': {'d': {'e': 3}}})
        3
        >>> get_data = iteratee('data')
        >>> get_data({'data': [1, 2, 3]})
        [1, 2, 3]
        >>> iteratee(['a.b'])({'a.b': 5})
        5
        >>> iteratee('a.b')({'a': {'b': 5}})
        5

    Args:
        obj (object): Object to convert into an iteratee.

    Returns:
        callable: Iteratee function.
    """
    if obj is None:
        return identity
    elif callable(obj):
        return obj
    elif isinstance(obj, dict):
        return conformance(obj)
    elif isinstance(obj, set):
        return pickgetter(obj)
    elif isinstance(obj, tuple):
        return atgetter(obj)
    else:
        return pathgetter(obj)


def negate(func):
    """
    Creates a function that negates the result of the predicate `func`.

    Examples:
        >>> not_number = negate(lambda x: isinstance(x, (int, float)))
        >>> not_number(1)
        False
        >>> not_number('1')
        True

    Args:
        func (callabe): Function to negate.

    Returns:
        function
    """
    return lambda *args, **kwargs: not func(*args, **kwargs)


def noop(*args, **kwargs):
    """
    A no-operation function.

    Examples:
        >>> noop(1, 2, 3) is None
        True
    """
    return


def over(*funcs):
    """
    Creates a function that calls each function with the provided arguments and returns the results
    as a ``tuple``.

    Example:
        >>> minmax = over(min, max)
        >>> minmax([1, 2, 3, 4])
        (1, 4)

    Args:
        *funcs (callable): Functions to call.

    Returns:
        callable: Function that returns tuple results from each function call.
    """
    return lambda *args: tuple(func(*args) for func in funcs)


def overall(*funcs):
    """
    Creates a function that returns ``True`` when all of the given functions return true for the
    provided arguments.

    Example:
        >>> is_bool = overall(
        ...     lambda v: isinstance(v, bool),
        ...     lambda v: v is True or v is False
        ... )
        >>> is_bool(False)
        True
        >>> is_bool(0)
        False

    Args:
        *funcs (callable): Functions to call.

    Returns:
        callable: Function that returns bool of whether call functions evaulate to true.
    """
    return lambda *args: all(func(*args) for func in funcs)


def overany(*funcs):
    """
    Creates a function that returns ``True`` when any of the given functions return true for the
    provided arguments.

    Example:
        >>> is_bool_like = overany(
        ...     lambda v: isinstance(v, bool),
        ...     lambda v: v in [0, 1]
        ... )
        >>> is_bool_like(False)
        True
        >>> is_bool_like(0)
        True

    Args:
        *funcs (callable): Functions to call.

    Returns:
        callable: Function that returns bool of whether call functions evaulate to true.
    """
    return lambda *args: any(func(*args) for func in funcs)


def pathgetter(path, default=None):
    """
    Creates a function that returns the value at path of a given object.

    Examples:
        >>> get_data = pathgetter('data')
        >>> get_data({'data': 1})
        1
        >>> get_data({}) is None
        True
        >>> get_first = pathgetter(0)
        >>> get_first([1, 2, 3])
        1
        >>> get_nested = pathgetter('data.items')
        >>> get_nested({'data': {'items': [1, 2]}})
        [1, 2]

    Args:
        path (object): Path value to fetch from object.

    Returns:
        callable: Function like ``f(obj): fnc.get(path, obj)``.
    """
    return partial(fnc.get, path, default=default)


def pickgetter(keys):
    """
    Creates a function that returns the value at path of a given object.

    Examples:
        >>> pick_ab = pickgetter(['a', 'b'])
        >>> pick_ab({'a': 1, 'b': 2, 'c': 4}) == {'a': 1, 'b': 2}
        True

    Args:
        keys (Iterable): Keys to fetch from object.

    Returns:
        callable: Function like ``f(obj): fnc.pick(keys, obj)``.
    """
    return partial(fnc.pick, keys)


def random(start=0, stop=1, floating=False):
    """
    Produces a random number between `start` and `stop` (inclusive). If only one argument is
    provided a number between 0 and the given number will be returned. If floating is truthy or
    either `start` or `stop` are floats a floating-point number will be returned instead of an
    integer.

    Args:
        start (int): Minimum value.
        stop (int): Maximum value.
        floating (bool, optional): Whether to force random value to ``float``. Default
            is ``False``.

    Returns:
        int|float: Random value.

    Example:
        >>> 0 <= random() <= 1
        True
        >>> 5 <= random(5, 10) <= 10
        True
        >>> isinstance(random(floating=True), float)
        True
    """
    floating = isinstance(start, float) or isinstance(stop, float) or floating is True

    if stop < start:
        stop, start = start, stop

    if floating:
        rnd = uniform(start, stop)
    else:
        rnd = randint(start, stop)

    return rnd


def retry(  # noqa: C901
    attempts=3,
    *,
    delay=0.5,
    max_delay=150.0,
    scale=2.0,
    jitter=0,
    exceptions=(Exception,),
    on_exception=None
):
    """
    Decorator that retries a function multiple times if it raises an exception with an optional
    delay between each attempt. When a `delay` is supplied, there will be a sleep period in between
    retry attempts. The first delay time will always be equal to `delay`. After subsequent retries,
    the delay time will be scaled by `scale` up to `max_delay`. If `max_delay` is ``0``, then
    `delay` can increase unbounded.

    Args:
        attempts (int, optional): Number of retry attempts. Defaults to ``3``.
        delay (int|float, optional): Base amount of seconds to sleep between retry
            attempts. Defaults to ``0.5``.
        max_delay (int|float, optional): Maximum number of seconds to sleep between
            retries. Is ignored when equal to ``0``. Defaults to ``150.0``
            (2.5 minutes).
        scale (int|float, optional): Scale factor to increase `delay` after first retry
            fails. Defaults to ``2.0``.
        jitter (int|float|tuple, optional): Random jitter to add to `delay` time. Can be
            a positive number or 2-item tuple of numbers representing the random range
            to choose from. When a number is given, the random range will be from
            ``[0, jitter]``. When jitter is a float or contains a float, then a random
            float will be chosen; otherwise, a random integer will be selected. Defaults
            to ``0`` which disables jitter.
        exceptions (tuple, optional): Tuple of exceptions that trigger a retry attempt.
            Exceptions not in the tuple will be ignored. Defaults to ``(Exception,)``
            (all exceptions).
        on_exception (function, optional): Function that is called when a retryable
            exception is caught. It is invoked with ``on_exception(exc, attempt)`` where
            ``exc`` is the caught exception and ``attempt`` is the attempt count. All
            arguments are optional. Defaults to ``None``.

    Example:

        >>> @retry(attempts=3, delay=0)
        ... def do_something():
        ...     print('something')
        ...     raise Exception('something went wrong')
        >>> try: do_something()
        ... except Exception: print('caught something')
        something
        something
        something
        caught something
    """
    if isinstance(exceptions, Exception):  # pragma: no cover
        exceptions = (exceptions,)

    if not isinstance(attempts, int) or attempts <= 0:
        raise ValueError("attempts must be an integer greater than 0")

    if not isinstance(delay, number_types) or delay < 0:
        raise ValueError("delay must be a number greater than or equal to 0")

    if not isinstance(max_delay, number_types) or max_delay < 0:
        raise ValueError("scale must be a number greater than or equal to 0")

    if not isinstance(scale, number_types) or scale <= 0:
        raise ValueError("scale must be a number greater than 0")

    if (
        not isinstance(jitter, number_types + (tuple,))
        or (isinstance(jitter, number_types) and jitter < 0)
        or (
            isinstance(jitter, tuple)
            and (len(jitter) != 2 or not all(isinstance(jit, number_types) for jit in jitter))
        )
    ):
        raise ValueError("jitter must be a number greater than 0 or a 2-item tuple of " "numbers")

    if not isinstance(exceptions, tuple) or not all(
        issubclass(exc, Exception) for exc in exceptions
    ):
        raise TypeError("exceptions must be a tuple of Exception types")

    if on_exception and not callable(on_exception):
        raise TypeError("on_exception must be a callable")

    if jitter and not isinstance(jitter, tuple):
        jitter = (0, jitter)

    def decorator(func):
        @wraps(func)
        def decorated(*args, **kargs):
            delay_time = delay

            for attempt in range(1, attempts + 1):
                # pylint: disable=catching-non-exception
                try:
                    return func(*args, **kargs)
                except exceptions as exc:
                    if on_exception:
                        exc.retry = {"attempt": attempt}
                        on_exception(exc)

                    if attempt == attempts:
                        raise

                    if jitter:
                        delay_time += max(0, random(*jitter))

                    if delay_time < 0:  # pragma: no cover
                        continue

                    if max_delay:
                        delay_time = min(delay_time, max_delay)

                    time.sleep(delay_time)

                    # Scale after first iteration.
                    delay_time *= scale

        return decorated

    return decorator
