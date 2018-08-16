"""General utility functions.
"""

from collections.abc import Iterable, Mapping, Sequence
from functools import partial, wraps
import itertools
from random import randint, uniform
import re
import time

import fnc

from .helpers import Sentinel, number_types


# These regexes are used in aspath() to parse deep path strings.

# This is used to split a deep path string into dict keys or list indexex.
# This matches "." as delimiter and "[<key>]" as delimiter while keeping the
# "[<key>]" as an item.
RE_PATH_KEY_DELIM = re.compile(r'(?<!\\)\.|(\[.*?\])')

# Matches on path strings like "[<key>]".
RE_PATH_GET_ITEM = re.compile(r'^\[.*?\]$')


def after(method):
    """Decorator that calls `method` after the decorated function is called.

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
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            method()
            return result
        return decorated
    return decorator


def aspath(value):
    """Converts value to an object path list.

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

    return [_parse_path_token(token)
            for token in RE_PATH_KEY_DELIM.split(value)
            if token]


def _parse_path_token(token):
    if RE_PATH_GET_ITEM.match(token):
        path = token[1:-1]
    else:
        path = token

    return path


def atgetter(paths):
    """Creates a function that returns the values at paths of a given object.

    Examples:
        >>> get_id_name = atgetter(['data.id', 'data.name'])
        >>> get_id_name({'data': {'id': 1, 'name': 'foo'}})
        (1, 'foo')

    Args:
        paths (Iterable): Path values to fetch from object.

    Returns:
        function: Function like ``f(obj): fnc.at(paths, obj)``.
    """
    return partial(fnc.at, paths)


def before(method):
    """Decorator that calls `method` before the decorated function is called.

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
        def decorated(*args, **kwargs):
            method()
            return func(*args, **kwargs)
        return decorated
    return decorator


def compose(*funcs):
    """Create a function that is the composition of the provided functions,
    where each successive invocation is supplied the return value of the
    previous. For example, composing the functions ``f()``, ``g()``, and
    ``h()`` produces ``h(g(f()))``.

    Examples:
        >>> mult_5 = lambda x: x * 5
        >>> div_10 = lambda x: x / 10.0
        >>> pow_2 = lambda x: x ** 2
        >>> mult_div_pow = compose(sum, mult_5, div_10, pow_2)
        >>> mult_div_pow([1, 2, 3, 4])
        25.0

    Args:
        *funcs (function): Function(s) to compose.

    Returns:
        function: Composed function.
    """
    def _compose(*args, **kwargs):
        result = None
        for func in funcs:
            result = func(*args, **kwargs)
            args, kwargs = (result,), {}
        return result
    return _compose


def constant(value):
    """Creates a function that returns a constant `value`.

    Examples:
        >>> pi = constant(3.14)
        >>> pi()
        3.14

    Args:
        value (object): Constant value to return.

    Returns:
        function: Function that always returns `value`.
    """
    return lambda *args, **kwargs: value


def identity(value=None, *args, **kwargs):
    """Return the first argument provided.

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


def ismatch(source, target):
    """Return whether the `target` object is a subset of `source` where
    `target` contains the same key-value pairs in `source`.

    Examples:
        >>> ismatch({'b': 2}, {'a': 1, 'b': 2})
        True
        >>> ismatch({'b': 3}, {'a': 1, 'b': 2})
        False

    Args:
        source (object): Object of path values to match.
        target (object): Object to compare.

    Returns:
        bool: Whether `target` is a match or not.
    """
    result = True
    for key, value in source.items():
        if fnc.get(key, target, default=Sentinel) != value:
            result = False
            break

    return result


def iteratee(obj):
    """Return iteratee function based on the type of `obj`.

    The iteratee object can be one of the following:

    - ``callable``: Return as-is.
    - ``None``: Return :func:`identity` function.
    - ``dict``: Return :func:`matches(obj)` function.
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
        function: Iteratee function.
    """
    if callable(obj):
        return obj
    elif obj is None:
        return identity
    elif isinstance(obj, dict):
        return matches(obj)
    elif isinstance(obj, set):
        return pickgetter(obj)
    elif isinstance(obj, tuple):
        return atgetter(obj)
    else:
        return pathgetter(obj)


def noop(*args, **kwargs):
    """A no-operation function.

    Examples:
        >>> noop(1, 2, 3) is None
        True
    """
    return


def matches(source):
    """Creates a function that does a shallow comparison between a given object
    and the `source` dictionary.

    Examples:
        >>> matches({'a': 1})({'b': 2, 'a': 1})
        True
        >>> matches({'a': 1})({'b': 2, 'a': 2})
        False

    Args:
        source (dict): Source object used for comparision.

    Returns:
        function
    """
    if not isinstance(source, dict):  # pragma: no cover
        raise TypeError('matches "source" must be a dict')

    return partial(ismatch, source)


def pathgetter(path, default=None):
    """Creates a function that returns the value at path of a given object.

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
        path (str|list): Path value to fetch from object.

    Returns:
        function: Function like ``f(obj): fnc.get(path, obj)``.
    """
    return partial(fnc.get, path, default=default)


def pickgetter(keys):
    """Creates a function that returns the value at path of a given object.

    Examples:
        >>> pick_ab = pickgetter(['a', 'b'])
        >>> pick_ab({'a': 1, 'b': 2, 'c': 4}) == {'a': 1, 'b': 2}
        True

    Args:
        keys (Iterable): Keys to fetch from object.

    Returns:
        function: Function like ``f(obj): fnc.pick(keys, obj)``.
    """
    return partial(fnc.pick, keys)


def random(start=0, stop=1, floating=False):
    """Produces a random number between `start` and `stop` (inclusive). If only
    one argument is provided a number between 0 and the given number will be
    returned. If floating is truthy or either `start` or `stop` are floats a
    floating-point number will be returned instead of an integer.

    Args:
        start (int): Minimum value.
        stop (int): Maximum value.
        floating (bool, optional): Whether to force random value to ``float``.
            Default is ``False``.

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
    floating = (isinstance(start, float) or
                isinstance(stop, float) or
                floating is True)

    if stop < start:
        stop, start = start, stop

    if floating:
        rnd = uniform(start, stop)
    else:
        rnd = randint(start, stop)

    return rnd


def retry(attempts=3, *,
          delay=0.5,
          max_delay=150.0,
          scale=2.0,
          jitter=0,
          exceptions=(Exception,),
          on_exception=None):
    """Decorator that retries a function multiple times if it raises an
    exception with an optional delay between each attempt.
    When a `delay` is supplied, there will be a sleep period in between retry
    attempts. The first delay time will always be equal to `delay`. After
    subsequent retries, the delay time will be scaled by `scale` up to
    `max_delay`. If `max_delay` is ``0``, then `delay` can increase unbounded.

    Args:
        attempts (int, optional): Number of retry attempts. Defaults to ``3``.
        delay (int|float, optional): Base amount of seconds to sleep between
            retry attempts. Defaults to ``0.5``.
        max_delay (int|float, optional): Maximum number of seconds to sleep
            between retries. Is ignored when equal to ``0``. Defaults to
            ``150.0`` (2.5 minutes).
        scale (int|float, optional): Scale factor to increase `delay` after
            first retry fails. Defaults to ``2.0``.
        jitter (int|float|tuple, optional): Random jitter to add to `delay`
            time. Can be a positive number or 2-item tuple of numbers
            representing the random range to choose from. When a number is
            given, the random range will be from ``[0, jitter]``. When jitter
            is a float or contains a float, then a random float will be chosen;
            otherwise, a random integer will be selected. Defaults to ``0``
            which disables jitter.
        exceptions (tuple, optional): Tuple of exceptions that trigger a retry
            attempt. Exceptions not in the tuple will be ignored. Defaults to
            ``(Exception,)`` (all exceptions).
        on_exception (function, optional): Function that is called when a
            retryable exception is caught. It is invoked with
            ``on_exception(exc, attempt)`` where ``exc`` is the caught
            exception and ``attempt`` is the attempt count. All arguments are
            optional. Defaults to ``None``.

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
        raise ValueError('attempts must be an integer greater than 0')

    if not isinstance(delay, number_types) or delay < 0:
        raise ValueError('delay must be a number greater than or equal to 0')

    if not isinstance(max_delay, number_types) or max_delay < 0:
        raise ValueError('scale must be a number greater than or equal to 0')

    if not isinstance(scale, number_types) or scale <= 0:
        raise ValueError('scale must be a number greater than 0')

    if (not isinstance(jitter, number_types + (tuple,)) or
            (isinstance(jitter, number_types) and jitter < 0) or
            (isinstance(jitter, tuple) and (
                len(jitter) != 2 or
                not all(isinstance(jit, number_types) for jit in jitter)))):
        raise ValueError(
            'jitter must be a number greater than 0 or a 2-item tuple of '
            'numbers')

    if (not isinstance(exceptions, tuple) or
            not all(issubclass(exc, Exception) for exc in exceptions)):
        raise TypeError('exceptions must be a tuple of Exception types')

    if on_exception and not callable(on_exception):
        raise TypeError('on_exception must be a callable')

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
                        exc.retry = {'attempt': attempt}
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
