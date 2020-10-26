"""
Functions that operate on sequences.

Most of these functions return generators so that they will be more efficient at processing large
datasets. All generator functions will have a ``Yields`` section in their docstring to easily
identify them as generators. Otherwise, functions that return concrete values with have a
``Returns`` section instead.
"""

from collections import Counter, deque
from functools import partial
import itertools
from operator import not_

import fnc

from .helpers import Container, iscollection, isgenerator


_filter = filter
_map = map


def chunk(size, seq):
    """
    Split elements of `seq` into chunks with length `size` and yield each chunk.

    Examples:
        >>> list(chunk(2, [1, 2, 3, 4, 5]))
        [[1, 2], [3, 4], [5]]

    Args:
        seq (Iterable): Iterable to chunk.
        size (int, optional): Chunk size. Defaults to ``1``.

    Yields:
        list: Chunked groups.
    """
    if not isinstance(size, int) or size <= 0:  # pragma: no cover
        raise ValueError("size must be an integer greater than zero")

    group = []

    for item in seq:
        if len(group) >= size:
            yield group
            group = []
        group.append(item)

    if group:
        yield group


def compact(seq):
    """
    Exclude elements from `seq` that are falsey.

    Examples:
        >>> list(compact(['', 1, 0, True, False, None]))
        [1, True]

    Args:
        seq (Iterable): Iterable to compact.

    Yields:
        Elements that are truthy.
    """
    for item in seq:
        if item:
            yield item


def concat(*seqs):
    """
    Concatenates zero or more iterables into a single iterable.

    Examples:
        >>> list(concat([1, 2], [3, 4], [[5], [6]]))
        [1, 2, 3, 4, [5], [6]]

    Args:
        *seqs (Iterable): Iterables to concatenate.

    Yields:
        Each element from all iterables.
    """
    return itertools.chain.from_iterable(seqs)


def countby(iteratee, seq):
    """
    Return a ``dict`` composed of keys generated from the results of running each element of `seq`
    through the `iteratee`.

    Examples:
        >>> result = countby(None, [1, 2, 1, 2, 3, 4])
        >>> result == {1: 2, 2: 2, 3: 1, 4: 1}
        True
        >>> result = countby(lambda x: x.lower(), ['a', 'A', 'B', 'b'])
        >>> result == {'a': 2, 'b': 2}
        True
        >>> result = countby('a', [{'a': 'x'}, {'a': 'x'}, {'a': 'y'}])
        >>> result == {'x': 2, 'y': 1}
        True

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to iterate over.

    Returns:
        dict
    """
    return dict(Counter(map(iteratee, seq)))


def difference(seq, *seqs):
    """
    Yields elements from `seq` that are not in `seqs`.

    Note:
        This function is like ``set.difference()`` except it works with both hashable
        and unhashable values and preserves the ordering of the original iterables.

    Examples:
        >>> list(difference([1, 2, 3], [1], [2]))
        [3]
        >>> list(difference([1, 4, 2, 3, 5, 0], [1], [2, 0]))
        [4, 3, 5]
        >>> list(difference([1, 3, 4, 1, 2, 4], [1, 4]))
        [3, 2]

    Args:
        seq (Iterable): Iterable to compute difference against.
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Each element in `seq` that doesn't appear in `seqs`.
    """
    yield from differenceby(None, seq, *seqs)


def differenceby(iteratee, seq, *seqs):
    """
    Like :func:`difference` except that an `iteratee` is used to modify each element in the
    sequences. The modified values are then used for comparison.

    Note:
        This function is like ``set.difference()`` except it works with both hashable
        and unhashable values and preserves the ordering of the original iterables.

    Examples:
        >>> list(differenceby('a', [{'a': 1}, {'a': 2}, {'a': 3}], [{'a': 1}], [{'a': 2}]))
        [{'a': 3}]
        >>> list(differenceby(lambda x: x % 4, [1, 4, 2, 3, 5, 0], [1], [2, 0]))
        [3]

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to compute difference against.
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Each element in `seq` that doesn't appear in `seqs`.
    """
    if not seqs:
        yield from unionby(iteratee, seq)
        return

    if iteratee is not None:
        iteratee = fnc.iteratee(iteratee)

    yielded = Container()
    # Concat sequences into a single sequence and map iteratee to each item so that the
    # computed value only needs to be done once for each item since that is what we'll
    # compare to below. We'll store these values into a iterable in case any of the
    # sequences are a generator/iterator that would get exhausted if we tried to iterate
    # over it more than once.
    others = Container(map(iteratee, concat(*seqs)))

    for item in seq:
        if iteratee is not None:
            value = iteratee(item)
        else:
            value = item

        if value in yielded or value in others:
            continue

        yield item
        yielded.add(value)


def duplicates(seq, *seqs):
    """
    Yields unique elements from sequences that are repeated one or more times.

    Note:
        The order of yielded elements depends on when the second duplicated
        element is found and not when the element first appeared.

    Examples:
        >>> list(duplicates([0, 1, 3, 2, 3, 1]))
        [3, 1]
        >>> list(duplicates([0, 1], [3, 2], [3, 1]))
        [3, 1]

    Args:
        seq (Iterable): Iterable to check for duplicates.
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Duplicated elements.
    """
    yield from duplicatesby(None, seq, *seqs)


def duplicatesby(iteratee, seq, *seqs):
    """
    Like :func:`duplicates` except that an `iteratee` is used to modify each element in the
    sequences. The modified values are then used for comparison.

    Examples:
        >>> list(duplicatesby('a', [{'a':1}, {'a':3}, {'a':2}, {'a':3}, {'a':1}]))
        [{'a': 3}, {'a': 1}]

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to check for duplicates
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Each element in `seq` that doesn't appear in `seqs`.
    """
    if iteratee is not None:
        iteratee = fnc.iteratee(iteratee)

    seen = Container()
    yielded = Container()

    for item in itertools.chain(seq, *seqs):
        if iteratee is not None:
            value = iteratee(item)
        else:
            value = item

        if value not in seen:
            seen.add(value)
            continue

        if value not in yielded:
            yield item
            yielded.add(value)


def filter(iteratee, seq):
    """
    Filter `seq` by `iteratee`, yielding only the elements that the iteratee returns truthy for.

    Note:
        This function is like the builtin ``filter`` except it converts `iteratee` into
        a fnc-style predicate.

    Examples:
        >>> result = filter({'a': 1}, [{'a': 1}, {'b': 2}, {'a': 1, 'b': 3}])
        >>> list(result) == [{'a': 1}, {'a': 1, 'b': 3}]
        True
        >>> list(filter(lambda x: x >= 3, [1, 2, 3, 4]))
        [3, 4]

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to filter.

    Yields:
        Filtered elements.
    """
    return _filter(fnc.iteratee(iteratee), seq)


def find(iteratee, seq):
    """
    Iterates over elements of `seq`, returning the first element that the iteratee returns truthy
    for.

    Examples:
        >>> find(lambda x: x >= 3, [1, 2, 3, 4])
        3
        >>> find(lambda x: x >= 5, [1, 2, 3, 4]) is None
        True
        >>> find({'a': 1}, [{'a': 1}, {'b': 2}, {'a': 1, 'b': 2}])
        {'a': 1}
        >>> result = find({'a': 1}, [{'b': 2}, {'a': 1, 'b': 2}, {'a': 1}])
        >>> result == {'a': 1, 'b': 2}
        True

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to iterate over.

    Returns:
        First element found or ``None``.
    """
    for item in filter(iteratee, seq):
        return item


def findindex(iteratee, seq):
    """
    Return the index of the element in `seq` that returns ``True`` for `iteratee`. If no match is
    found, ``-1`` is returned.

    Examples:
        >>> findindex(lambda x: x >= 3, [1, 2, 3, 4])
        2
        >>> findindex(lambda x: x > 4, [1, 2, 3, 4])
        -1

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to process.

    Returns:
        int: Index of found item or ``-1`` if not found.
    """
    iteratee = fnc.iteratee(iteratee)
    return next((i for i, value in enumerate(seq) if iteratee(value)), -1)


def findlast(iteratee, seq):
    """
    This function is like :func:`find` except it iterates over elements of `seq` from right to left.

    Examples:
        >>> findlast(lambda x: x >= 3, [1, 2, 3, 4])
        4
        >>> findlast(lambda x: x >= 5, [1, 2, 3, 4]) is None
        True
        >>> result = findlast({'a': 1}, [{'a': 1}, {'b': 2}, {'a': 1, 'b': 2}])
        >>> result == {'a': 1, 'b': 2}
        True

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to iterate over.

    Returns:
        Last element found or ``None``.
    """
    return find(iteratee, reversed(seq))


def findlastindex(iteratee, seq):
    """
    Return the index of the element in `seq` that returns ``True`` for `iteratee`. If no match is
    found, ``-1`` is returned.

    Examples:
        >>> findlastindex(lambda x: x >= 3, [1, 2, 3, 4])
        3
        >>> findlastindex(lambda x: x > 4, [1, 2, 3, 4])
        -1

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to process.

    Returns:
        int: Index of found item or ``-1`` if not found.
    """
    iteratee = fnc.iteratee(iteratee)
    return next((i for i, value in reversed(tuple(enumerate(seq))) if iteratee(value)), -1)


def flatten(*seqs):
    """
    Flatten iterables a single level deep.

    Examples:
        >>> list(flatten([[1], [2, [3]], [[4]]]))
        [1, 2, [3], [4]]
        >>> list(flatten([[1], [2, [3]], [[4]]], [5, [6, 7]]))
        [1, 2, [3], [4], 5, 6, 7]

    Args:
        *seqs (Iterables): Iterables to flatten.

    Yields:
        Eelements from the flattened iterable.
    """
    for item in itertools.chain.from_iterable(seqs):
        if iscollection(item):
            yield from item
        else:
            yield item


def flattendeep(*seqs):
    """
    Recursively flatten iterables.

    Examples:
        >>> list(flattendeep([[1], [2, [3]], [[4]]]))
        [1, 2, 3, 4]
        >>> list(flattendeep([[1], [2, [3]], [[4]]], [5, [6, 7]]))
        [1, 2, 3, 4, 5, 6, 7]
        >>> list(flattendeep([[1], [2, [3]], [[4]]], [5, [[[[6, [[[7]]]]]]]]))
        [1, 2, 3, 4, 5, 6, 7]

    Args:
        *seqs (Iterables): Iterables to flatten.

    Yields:
        Flattened elements.
    """
    for item in itertools.chain.from_iterable(seqs):
        if iscollection(item):
            yield from flattendeep(item)
        else:
            yield item


def groupall(iteratees, seq):
    """
    This function is like :func:`groupby` except it supports nested grouping by multiple iteratees.
    If only a single iteratee is given, it is like calling :func:`groupby`.

    Examples:
        >>> result = groupall(
        ...     ['shape', 'qty'],
        ...     [
        ...         {'shape': 'square', 'color': 'red', 'qty': 5},
        ...         {'shape': 'square', 'color': 'blue', 'qty': 10},
        ...         {'shape': 'square', 'color': 'orange', 'qty': 5},
        ...         {'shape': 'circle', 'color': 'yellow', 'qty': 5},
        ...         {'shape': 'circle', 'color': 'pink', 'qty': 10},
        ...         {'shape': 'oval', 'color': 'purple', 'qty': 5}
        ...     ]
        ... )
        >>> expected = {
        ...     'square': {
        ...         5: [
        ...             {'shape': 'square', 'color': 'red', 'qty': 5},
        ...             {'shape': 'square', 'color': 'orange', 'qty': 5}
        ...         ],
        ...         10: [{'shape': 'square', 'color': 'blue', 'qty': 10}]
        ...     },
        ...     'circle': {
        ...         5: [{'shape': 'circle', 'color': 'yellow', 'qty': 5}],
        ...         10: [{'shape': 'circle', 'color': 'pink', 'qty': 10}]
        ...     },
        ...     'oval': {
        ...         5: [{'shape': 'oval', 'color': 'purple', 'qty': 5}]
        ...     }
        ... }
        >>> result == expected
        True

    Args:
        iteratees (Iterable): Iteratees to group by.
        seq (Iterable): Iterable to iterate over.

    Returns:
        dict: Results of recursively grouping by all `iteratees`.
    """
    if not iteratees:
        return seq

    head, *rest = iteratees

    return fnc.mapvalues(partial(groupall, rest), groupby(head, seq))


def groupby(iteratee, seq):
    """
    Return a ``dict`` composed of keys generated from the results of running each element of `seq`
    through the `iteratee`.

    Examples:
        >>> result = groupby('a', [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])
        >>> result == {1: [{'a': 1, 'b': 2}], 3: [{'a': 3, 'b': 4}]}
        True
        >>> result = groupby({'a': 1}, [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])
        >>> result == {False: [{'a': 3, 'b': 4}], True: [{'a': 1, 'b': 2}]}
        True

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to iterate over.

    Returns:
        dict: Results of grouping by `iteratee`.
    """
    result = {}
    iteratee = fnc.iteratee(iteratee)

    for item in seq:
        result.setdefault(iteratee(item), []).append(item)

    return result


def intercalate(value, seq):
    """
    Insert `value` between each element in `seq` and concatenate the results.

    Examples:
        >>> list(intercalate('x', [1, [2], [3], 4]))
        [1, 'x', 2, 'x', 3, 'x', 4]
        >>> list(intercalate(', ', ['Lorem', 'ipsum', 'dolor']))
        ['Lorem', ', ', 'ipsum', ', ', 'dolor']
        >>> ''.join(intercalate(', ', ['Lorem', 'ipsum', 'dolor']))
        'Lorem, ipsum, dolor'
        >>> list(intercalate([0,0,0], [[1,2,3],[4,5,6],[7,8,9]]))
        [1, 2, 3, 0, 0, 0, 4, 5, 6, 0, 0, 0, 7, 8, 9]

    Args:
        value (object): Element to insert.
        seq (Iterable): Iterable to intercalate.

    Yields:
        Elements of the intercalated iterable.
    """
    return flatten(intersperse(value, seq))


def interleave(*seqs):
    """
    Merge multiple iterables into a single iterable by inserting the next element from each iterable
    by sequential round-robin.

    Examples:
        >>> list(interleave([1, 2, 3], [4, 5, 6], [7, 8, 9]))
        [1, 4, 7, 2, 5, 8, 3, 6, 9]

    Args:
        *seqs (Iterable): Iterables to interleave.

    Yields:
        Elements of the interleaved iterable.
    """
    queue = deque(iter(seq) for seq in seqs)

    while queue:
        seq = queue.popleft()

        try:
            yield next(seq)
        except StopIteration:
            pass
        else:
            queue.append(seq)


def intersection(seq, *seqs):
    """
    Computes the intersection of all the passed-in iterables.

    Note:
        This function is like ``set.intersection()`` except it works with both hashable
        and unhashable values and preserves the ordering of the original iterables.

    Examples:
        >>> list(intersection([1, 2, 3], [1, 2, 3, 4, 5], [2, 3]))
        [2, 3]
        >>> list(intersection([1, 2, 3]))
        [1, 2, 3]

    Args:
        seq (Iterable): Iterable to compute intersection against.
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Elements that itersect.
    """
    yield from intersectionby(None, seq, *seqs)


def intersectionby(iteratee, seq, *seqs):
    """
    Like :func:`intersection` except that an `iteratee` is used to modify each element in the
    sequences. The modified values are then used for comparison.

    Note:
        This function is like ``set.intersection()`` except it works with both hashable
        and unhashable values and preserves the ordering of the original iterables.

    Examples:
        >>> list(intersectionby(
        ...     'a',
        ...     [{'a': 1}, {'a': 2}, {'a': 3}],
        ...     [{'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}, {'a': 5}],
        ...     [{'a': 2}, {'a': 3}]
        ... ))
        [{'a': 2}, {'a': 3}]

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to compute intersection against.
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Elements that intersect.
    """
    if not seqs:
        yield from unionby(iteratee, seq)
        return

    if iteratee is not None:
        iteratee = fnc.iteratee(iteratee)

    yielded = Container()
    # Map iteratee to each item in each other sequence and compute intersection of those
    # values to reduce number of times iteratee is called. The resulting sequence will
    # be an intersection of computed values which will be used to compare to the primary
    # sequence. We'll store these values into a iterable in case any of the sequences
    # are a generator/iterator that would get exhausted if we tried to iterate over it
    # more than once.
    others = Container(intersection(*(map(iteratee, other) for other in seqs)))

    for item in seq:
        if iteratee is not None:
            value = iteratee(item)
        else:
            value = item

        if value in yielded:
            continue

        if value in others:
            yield item
            yielded.add(value)


def intersperse(value, seq):
    """
    Insert a separating element between each element in `seq`.

    Examples:
        >>> list(intersperse('x', [1, [2], [3], 4]))
        [1, 'x', [2], 'x', [3], 'x', 4]

    Args:
        value (object): Element to insert.
        seq (Iterable): Iterable to intersperse.

    Yields:
        Elements of the interspersed iterable.
    """
    seq = iter(seq)

    try:
        yield next(seq)
    except StopIteration:
        return

    for item in seq:
        yield value
        yield item


def keyby(iteratee, seq):
    """
    Return a ``dict`` composed of keys generated from the results of running each element of `seq`
    through the `iteratee`.

    Examples:
        >>> results = keyby('a', [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}])
        >>> results == {1: {'a': 1, 'b': 2}, 3: {'a': 3, 'b': 4}}
        True

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to iterate over.

    Returns:
        dict: Results of indexing by `iteratee`.
    """
    iteratee = fnc.iteratee(iteratee)
    return {iteratee(value): value for value in seq}


def map(iteratee, *seqs):
    """
    Map `iteratee` to each element of iterable and yield the results. If additional iterable
    arguments are passed, `iteratee` must take that many arguments and is applied to the items from
    all iterables in parallel.

    Note:
        This function is like the builtin ``map`` except it converts `iteratee` into a
        fnc-style predicate.

    Examples:
        >>> list(map(str, [1, 2, 3, 4]))
        ['1', '2', '3', '4']
        >>> list(map('a', [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}]))
        [1, 3, 5]
        >>> list(map('0.1', [[[0, 1]], [[2, 3]], [[4, 5]]]))
        [1, 3, 5]
        >>> list(map('a.b', [{'a': {'b': 1}}, {'a': {'b': 2}}]))
        [1, 2]
        >>> list(map('a.b[1]', [{'a': {'b': [0, 1]}}, {'a': {'b': [2, 3]}}]))
        [1, 3]

    Args:
        iteratee (object): Iteratee applied per iteration.
        *seqs (Iterable): Iterables to map.

    Yields:
        Mapped elements.
    """
    return _map(fnc.iteratee(iteratee), *seqs)


def mapcat(iteratee, *seqs):
    """
    Map an `iteratee` to each element of each iterable in `seqs` and concatenate the results into a
    single iterable.

    Examples:
        >>> list(mapcat(lambda x: list(range(x)), range(4)))
        [0, 0, 1, 0, 1, 2]

    Args:
        iteratee (object): Iteratee to apply to each element.
        *seqs (Iterable): Iterable to map and concatenate.

    Yields:
        Elements resulting from concat + map operations.
    """
    return concat(*map(iteratee, *seqs))


def mapflat(iteratee, *seqs):
    """
    Map an `iteratee` to each element of each iterable in `seqs` and flatten the results.

    Examples:
        >>> list(mapflat(lambda n: [[n, n]], [1, 2]))
        [[1, 1], [2, 2]]

    Args:
        iteratee (object): Iteratee applied per iteration.
        *seqs (Iterable): Iterables to iterate over.

    Yields:
        Elements result from flatten + map operations.
    """
    return flatten(map(iteratee, *seqs))


def mapflatdeep(iteratee, *seqs):
    """
    Map an `iteratee` to each element of each iterable in `seqs` and recurisvely flatten the
    results.

    Examples:
        >>> list(mapflatdeep(lambda n: [[n, n]], [1, 2]))
        [1, 1, 2, 2]

    Args:
        iteratee (object): Iteratee applied per iteration.
        *seqs (Iterable): Iterables to iterate over.

    Yields:
        Elements result from recursive flatten + map operations.
    """
    return flattendeep(map(iteratee, *seqs))


def partition(iteratee, seq):
    """
    Return a ``tuple`` of 2 lists containing elements from `seq` split into two groups where the
    first group contains all elements the `iteratee` returned truthy for and the second group
    containing the falsey elements.

    Examples:
        >>> partition(lambda x: x % 2, [1, 2, 3, 4])
        ([1, 3], [2, 4])

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to iterate over.

    Returns:
        tuple[list]
    """
    iteratee = fnc.iteratee(iteratee)
    successes = []
    failures = []

    for item in seq:
        if iteratee(item):
            successes.append(item)
        else:
            failures.append(item)

    return successes, failures


def reject(iteratee, seq):
    """
    The opposite of :func:`filter` this function yields the elements of `seq` that the `iteratee`
    returns falsey for.

    Examples:
        >>> list(reject(lambda x: x >= 3, [1, 2, 3, 4]))
        [1, 2]
        >>> list(reject('a', [{'a': 0}, {'a': 1}, {'a': 2}]))
        [{'a': 0}]
        >>> list(reject({'a': 1}, [{'a': 0}, {'a': 1}, {'a': 2}]))
        [{'a': 0}, {'a': 2}]

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to iterate over.

    Yields:
        Rejected elements.
    """
    iteratee = fnc.iteratee(iteratee)
    return filter(fnc.compose(iteratee, not_), seq)


def union(seq, *seqs):
    """
    Computes the union of the passed-in iterables (sometimes referred to as ``unique``).

    Note:
        This function is like ``set.union()`` except it works with both hashable and
        unhashable values and preserves the ordering of the original iterables.

    Examples:
        >>> list(union([1, 2, 3, 1, 2, 3]))
        [1, 2, 3]
        >>> list(union([1, 2, 3], [2, 3, 4], [3, 4, 5]))
        [1, 2, 3, 4, 5]

    Args:
        seq (Iterable): Iterable to compute union against.
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Each unique element from all iterables.
    """
    yield from unionby(None, seq, *seqs)


def unionby(iteratee, seq, *seqs):
    """
    Like :func:`union` except that an `iteratee` is used to modify each element in the sequences.
    The modified values are then used for comparison.

    Note:
        This function is like ``set.union()`` except it works with both hashable and
        unhashable values and preserves the ordering of the original iterables.

    Examples:
        >>> list(unionby(
        ...     'a',
        ...     [{'a': 1}, {'a': 2}, {'a': 3}, {'a': 1}, {'a': 2}, {'a': 3}]
        ... ))
        [{'a': 1}, {'a': 2}, {'a': 3}]

    Args:
        iteratee (object): Iteratee applied per iteration.
        seq (Iterable): Iterable to compute union against.
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Each unique element from all iterables.
    """
    if iteratee is not None:
        iteratee = fnc.iteratee(iteratee)

    seen = Container()

    for item in itertools.chain(seq, *seqs):
        if iteratee is not None:
            value = iteratee(item)
        else:
            value = item

        if value not in seen:
            yield item

        seen.add(value)


def unzip(seq):
    """
    The inverse of the builtin ``zip`` function, this method transposes groups of elements into new
    groups composed of elements from each group at their corresponding indexes.

    Examples:
        >>> list(unzip([(1, 4, 7), (2, 5, 8), (3, 6, 9)]))
        [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        >>> list(unzip(unzip([(1, 4, 7), (2, 5, 8), (3, 6, 9)])))
        [(1, 4, 7), (2, 5, 8), (3, 6, 9)]

    Args:
        seq (Iterable): Iterable to unzip.

    Yields:
        tuple: Each transposed group.
    """
    return zip(*seq)


def without(values, seq):
    """
    Exclude elements in `seq` that are in `values`.

    Examples:
        >>> list(without([2, 4], [1, 2, 3, 2, 4, 4, 3]))
        [1, 3, 3]

    Args:
        values (mixed): Values to remove.
        seq (Iterable): List to filter.

    Yields:
        Elements not in `values`.
    """
    for item in seq:
        if item not in values:
            yield item


def xor(seq, *seqs):
    """
    Computes the symmetric difference of the provided iterables where the elements are only in one
    of the iteralbes.

    Note:
        This function is like ``set.symmetric_difference()`` except it works with both
        hashable and unhashable values and preserves the ordering of the original
        iterables.

    Warning:
        While this function returns a generator object, internally it will create
        intermediate non-generator iterables which may or may not be a performance
        concern depending on the sizes of the inputs.

    Examples:
        >>> list(xor([1, 3, 4], [1, 2, 4], [2]))
        [3]

    Args:
        seq (Iterable): Iterable to compute symmetric difference against.
        *seqs (Iterable): Other iterables to compare with.

    Yields:
        Elements from the symmetric difference.
    """
    if not seqs:
        yield from seq
        return

    head, *rest = seqs

    if isgenerator(seq):
        seq = tuple(seq)

    if isgenerator(head):
        head = tuple(head)

    a = union(seq, head)
    b = tuple(intersection(seq, head))
    d = difference(a, b)

    yield from xor(d, *rest)
