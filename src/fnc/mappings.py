"""Functions that operate on mappings.

A mapping includes dictionaries, lists, strings, ``collections.abc.Mapping``
and ``collections.abc.Sequence`` subclasses, and other mapping-like objects
that either have an ``items()`` method, have ``keys()`` and ``__getitem__``
methods, or have an ``__iter__()`` method. For functions that use :func:`get`,
non-mapping object values can be selected from class attributes.
"""

from collections.abc import Mapping, Sequence

import fnc

from .helpers import NotSet, Sentinel, iterate


def at(paths, obj):
    """Creates a ``tuple`` of elements from `obj` at the given `paths`.

    Examples:
        >>> at(['a', 'c'], {'a': 1, 'b': 2, 'c': 3, 'd': 4})
        (1, 3)
        >>> at(['a', ['c', 'd', 'e']], {'a': 1, 'b': 2, 'c': {'d': {'e': 3}}})
        (1, 3)
        >>> at(['a', 'c.d.e[0]'], {'a': 1, 'b': 2, 'c': {'d': {'e': [3]}}})
        (1, 3)
        >>> at([0, 2], [1, 2, 3, 4])
        (1, 3)

    Args:
        collection (Iterable): Iterable to pick from.
        paths (Iterable): The object paths to pick.

    Returns:
        tuple
    """
    return tuple(get(path, obj) for path in paths)


def defaults(*objs):
    """Create a ``dict`` extended with the key-values from the provided
    dictionaries such that keys are set once and not overridden by subsequent
    dictionaries.

    Examples:
        >>> obj = defaults({'a': 1}, {'b': 2}, {'c': 3, 'b': 5}, \
                           {'a': 4, 'c': 2})
        >>> obj == {'a': 1, 'b': 2, 'c': 3}
        True

    Args:
        *objs (dict): Dictionary sources.

    Returns:
        dict
    """
    return merge(*reversed(objs))


def get(path, obj, *, default=None):
    """Get the `path` value at any depth of an object. If path doesn't exist,
    `default` is returned.

    Examples:
        >>> get('a.b.c', {}) is None
        True
        >>> get('a.b.c[1]', {'a': {'b': {'c': [1, 2, 3, 4]}}})
        2
        >>> get('a.b.c.1', {'a': {'b': {'c': [1, 2, 3, 4]}}})
        2
        >>> get('a.b.1.c[1]', {'a': {'b': [0, {'c': [1, 2]}]}})
        2
        >>> get(['a', 'b', 1, 'c', 1], {'a': {'b': [0, {'c': [1, 2]}]}})
        2
        >>> get('a.b.1.c.2', {'a': {'b': [0, {'c': [1, 2]}]}}, default=False)
        False

    Args:
        path (object): Path to test for. Can be a key value, list of keys, or a
            ``.`` delimited path-string.
        obj (Mapping): Object to process.

    Keyword Arguments:
        default (mixed): Default value to return if path doesn't exist.
            Defaults to ``None``.

    Returns:
        object: Value of `obj` at path.
    """
    if default is NotSet:
        # When NotSet given for default, then this method will raise if path is
        # not present in obj.
        sentinel = NotSet
    else:
        # When a returnable default is given, use a sentinel value to detect
        # when _get() returns a default value for a missing path so we can exit
        # early from the loop and not mistakenly iterate over the default.
        sentinel = Sentinel

    result = obj
    for key in fnc.aspath(path):
        result = _get(key, result, default=sentinel)

        if result is sentinel:
            result = default
            break

    return result


def _get(key, obj, *, default=NotSet):
    # Try item getter.
    try:
        return obj[key]
    except (KeyError, TypeError, IndexError):
        pass

    # Try integer indexed item getter.
    try:
        return obj[int(key)]
    except (KeyError, TypeError, IndexError, ValueError):
        pass

    # Try attribute access but only if obj isn't a mapping or sequence.
    if not isinstance(obj, (Mapping, Sequence)) or isinstance(obj, tuple):
        try:
            return getattr(obj, key)
        except AttributeError:
            pass

    if default is NotSet:
        raise KeyError('Key {!r} not found in {!r}'.format(obj, key))

    return default


def has(path, obj):
    """Return whether `path` exists in `obj`.

    Examples:
        >>> has(1, [1, 2, 3])
        True
        >>> has('b', {'a': 1, 'b': 2})
        True
        >>> has('c', {'a': 1, 'b': 2})
        False
        >>> has('a.b[1].c[1]', {'a': {'b': [0, {'c': [1, 2]}]}})
        True
        >>> has('a.b.1.c.2', {'a': {'b': [0, {'c': [1, 2]}]}})
        False

    Args:
        path (object): Path to test for. Can be a key value, list of keys, or a
            ``.`` delimited path-string.
        obj (Mapping): Object to test.

    Returns:
        bool: Whether `obj` has `path`.
    """
    try:
        get(path, obj, default=NotSet)
        return True
    except KeyError:
        return False


def invert(obj):
    """Return a ``dict`` composed of the inverted keys and values of the given
    dictionary.

    Note:
        It's assumed that `obj` values are hashable as ``dict`` keys.

    Examples:
        >>> result = invert({'a': 1, 'b': 2, 'c': 3})
        >>> result == {1: 'a', 2: 'b', 3: 'c'}
        True

    Args:
        obj (Mapping): Mapping to invert.

    Returns:
        dict: Inverted dictionary.
    """
    return {value: key for key, value in iterate(obj)}


def mapkeys(iteratee, obj):
    """Return a ``dict`` with keys from `obj` mapped with `iteratee` while
    containing the same values.

    Examples:
        >>> result = mapkeys(lambda k: k * 2, {'a': 1, 'b': 2, 'c': 3})
        >>> result == {'aa': 1, 'bb': 2, 'cc': 3}
        True

    Args:
        iteratee (object): Iteratee applied to each key.
        obj (Mapping): Mapping to map.

    Returns:
        dict: Dictionary with mapped keys.
    """
    iteratee = fnc.iteratee(iteratee)
    return {iteratee(key): value for key, value in iterate(obj)}


def mapvalues(iteratee, obj):
    """Return a ``dict`` with values from `obj` mapped with `iteratee` while
    containing the same keys.

    Examples:
        >>> result = mapvalues(lambda v: v * 2, {'a': 1, 'b': 2, 'c': 3})
        >>> result == {'a': 2, 'b': 4, 'c': 6}
        True
        >>> result = mapvalues({'d': 4}, {'a': 1, 'b': {'d': 4}, 'c': 3})
        >>> result == {'a': False, 'b': True, 'c': False}
        True

    Args:
        iteratee (object): Iteratee applied to each key.
        obj (Mapping): Mapping to map.

    Returns:
        dict: Dictionary with mapped values.
    """
    iteratee = fnc.iteratee(iteratee)
    return {key: iteratee(value) for key, value in iterate(obj)}


def merge(*objs):
    """Create a ``dict`` merged with the key-values from the provided
    dictionaries such that each next dictionary extends the previous results.

    Examples:
        >>> obj = merge({'a': 0}, {'b': 1}, {'b': 2, 'c': 3}, {'a': 1})
        >>> obj == {'a': 1, 'b': 2, 'c': 3}
        True

    Args:
        *objs (dict): Dictionary sources.

    Returns:
        dict
    """
    result = {}
    for obj in objs:
        result.update(obj)
    return result


def omit(keys, obj):
    """The opposite of :func:`pick`. This method creates an object composed of
    the property paths of `obj` that are not omitted.

    Examples:
        >>> omit(['a', 'c'], {'a': 1, 'b': 2, 'c': 3 }) == {'b': 2}
        True
        >>> omit([0, 3], ['a', 'b', 'c', 'd']) == {1: 'b', 2: 'c'}
        True

    Args:
        keys (Iterable): Keys to omit.
        obj (Mapping): Object to process.

    Returns:
        dict: Dictionary with `keys` omitted.
    """
    return {key: value for key, value in iterate(obj) if key not in keys}


def pick(keys, obj):
    """Create a ``dict`` composed of the picked `keys` from `obj`.

    Examples:
        >>> pick(['a', 'b'], {'a': 1, 'b': 2, 'c': 3}) == {'a': 1, 'b': 2}
        True
        >>> pick(['a', 'b'], {'b': 2}) == {'b': 2}
        True

    Args:
        keys (Iterable): Keys to omit.
        obj (Mapping): Object to process.

    Returns:
        dict: Dict containg picked properties.
    """
    items = []
    for key in keys:
        value = _get(key, obj, default=Sentinel)
        if value is not Sentinel:
            items.append((key, value))
    return dict(items)
