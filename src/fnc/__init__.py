"""
The ``fnc`` library is a functional-style utility library with an emphasis on using generators to
process sequences of data. This allows one to easily build data processing pipelines to more
efficiently munge data through function composition.

All public functions are available from the main module.

::

    import fnc

    fnc.<function>

Note:
    It is recommended to use the above syntax or import functions from the main module instead of
    importing from submodules. Future versions may change/reorganize things which could break that
    usage.

So what makes this library different than other function libraries for Python? Some main features to
highlight are:

1. Generators when possible.
2. Shorthand iteratee support.
3. Shorthand partial function composition support.

Generators
----------

By using generators, large datasets can be processed more efficiently which can enable one to build
data pipelines that "push" each item of a sequence all the way through to the end before being
"collected" in a final data structure. This means that these data pipelines can iterate over a
sequence just once while transforming the data as it goes. These pipelines can be built through
function composition (e.g. ``fnc.compose`` + ``functools.partial``) or by simply building up the
final form through successive generator passing.

Iteratees
---------

The other main feature is shorthand iteratee support. But what is an iteratee? From Wikipedia
(https://en.wikipedia.org/wiki/Iteratee):

    ...an iteratee is a composable abstraction for incrementally processing sequentially
    presented chunks of input data in a purely functional fashion.

What does that mean exactly? An iteratee is a function that is applied to each item in a sequence.

Note:
    All functions that accept an iteratee have the iteratee as the first argument to the function.
    This mirrors the Python standard library for functions like ``map``, ``filter``, and ``reduce``.
    It also makes it easier to use ``functools.partial`` to create ad-hoc functions with bound
    iteratees.

Functions that accept iteratees can of course use a callable as the iteratee, but they can also
accept the shorthand styles below.

Note:
    If iteratee shorthand styles are not your thing, each shorthand style has a corresponding
    higher-order function that can be used to return the same callable iteratee.

Dict
++++

A dictionary-iteratee returns a "conforms" comparator that matches source key-values to
target key-values. Typically, this iteratee is used to filter a list of dictionaries by checking if
the targets are a superset of the source.

For example:

::

    x = [*fnc.filter({'a': 1, 'b': 2}, [{'a': 1}, {'a': 1, 'b': 2, 'c': 3}])]
    x == [{'a': 1, 'b': 2, 'c': 3}]

which is the same as:

::

    x = list(fnc.filter(fnc.conformance({'a': 1, 'b': 2}), ...))

Note:
    When values in the dictionary-iteratee are callables, they will be treated as predicate
    functions that will be called with the corresponding value in the comparison target.

Set
+++

A set-iteratee applies a "pickgetter" function to select a subset of fields from an object.

For example:

::

    x = [*fnc.map({'a', 'b'}, [{'a': 1, 'b': 2, 'c': 3}, {'b': 4, 'd': 5}, {'a': 1}])]
    x == [{'a': 1, 'b': 2}, {'a': None, 'b': 4}, {'a': 1, 'b': None}]

which is the same as:

::

    x = [*fnc.map(fnc.pickgetter(['a', 'b']), ...)]

    # or
    from functools import partial
    x = [*fnc.map(partial(fnc.pick, ['a', 'b']), ...)]

Tuple
+++++

A tuple-iteratee applies an "atgetter" function to return a tuple of values at the given paths.

For example:

::

    x = [
        *fnc.map(
            ('a', 'b'),
            [{'a': 1, 'b': 2, 'c': 3}, {'b': 4, 'd': 5}, {'a': 1}]
        )
    ]
    x == [(1, 2), (None, 4), (1, None)]

which is the same as:

::

    x = [*fnc.map(fnc.atgetter(['a', 'b']), ...)]

    # or
    x = [*fnc.map(partial(fnc.at, ['a', 'b']), ...)]

List
++++

A list-iteratee applies a "pathgetter" function to return the value at the given object path.

For example:

::

    x = [
        *fnc.map(
            ['a', 'aa', 0, 'aaa'],
            [{'a': {'aa': [{'aaa': 1}]}}, {'a': {'aa': [{'aaa': 2}]}}]
        )
    ]
    x == [1, 2]

which is the same as:

::

    x = [*fnc.map(fnc.pathgetter(['a', 'aa', 0, 'aaa']), ...)]

    # or
    x = [*fnc.map(partial(fnc.get, ['a', 'aa', 0, 'aaa']), ...)]

String
++++++

A string-iteratee is like a list-iteratee except that an object path is represented in object-path
notation like ``'a.aa[0].aaa'``.

For example:

::

    x = [
        *fnc.map(
            'a.aa[0].aaa',
            [{'a': {'aa': [{'aaa': 1}]}}, {'a': {'aa': [{'aaa': 2}]}}]
        )
    ]
    x == [1, 2]

which is the same as:

::

    x = [*fnc.map(fnc.pathgetter('a.aa[0].aaa'), ...)]

    # or
    x = [*fnc.map(partial(fnc.get, 'a.aa[0].aaa'), ...)]

Other Values
++++++++++++

All other non-callable values will be used in a "pathgetter" iteratee as a top-level "key" to return
the object value from. Callable values will be used directly as iteratees.

Note:
    To reference a mapping that has a ``tuple`` key (e.g. {(1, 2): 'value}), use the list-iteratee
    like ``fnc.map([(1, 2)], ...)``.


Function Composition
--------------------

The primary method for function composition is ``fnc.compose`` combined with "partial" shorthand as
needed.

What is "partial" shorthand? Instead of passing callables to ``fnc.compose``, one can pass a tuple
with the same arguments to ``functools.partial``.

::

    count_by_age_over21 = fnc.compose(
        (fnc.filter, {'age': lambda age: age >= 21}),
        (fnc.countby, 'age')
    )

    # is equivalent to...
    # count_by_age_over21 = fnc.compose(
    #     partial(fnc.filter, {'age': lambda age: age >= 21}),
    #     partial(fnc.countby, 'age')
    # )

    x = count_by_age_over21(
        [
            {'age': 20},
            {'age': 21},
            {'age': 30},
            {'age': 22},
            {'age': 21},
            {'age': 22}
        ]
    )
    x == {21: 2, 30: 1, 22: 2}

Note:
    The "partial" shorthand only supports invoking ``functools.partial`` using positional arguments.
    If keyword argument partials are needed, then use ``functools.partial`` directly.
"""

__version__ = "0.5.3"

from .mappings import at, defaults, get, has, invert, mapkeys, mapvalues, merge, omit, pick
from .sequences import (
    chunk,
    compact,
    concat,
    countby,
    difference,
    differenceby,
    duplicates,
    duplicatesby,
    filter,
    find,
    findindex,
    findlast,
    findlastindex,
    flatten,
    flattendeep,
    groupall,
    groupby,
    intercalate,
    interleave,
    intersection,
    intersectionby,
    intersperse,
    keyby,
    map,
    mapcat,
    mapflat,
    mapflatdeep,
    partition,
    reject,
    union,
    unionby,
    unzip,
    without,
    xor,
)
from .utilities import (
    after,
    aspath,
    atgetter,
    before,
    compose,
    conformance,
    conforms,
    constant,
    identity,
    iteratee,
    negate,
    noop,
    over,
    overall,
    overany,
    pathgetter,
    pickgetter,
    random,
    retry,
)
