"""The fnc package.

Functional utilities
"""

from .__version__ import __version__


from .mappings import (
    at,
    defaults,
    get,
    has,
    invert,
    mapkeys,
    mapvalues,
    merge,
    omit,
    pick
)

from .sequences import (
    chunk,
    compact,
    concat,
    countby,
    difference,
    duplicates,
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
    intersperse,
    keyby,
    map,
    mapcat,
    mapflat,
    mapflatdeep,
    partition,
    reject,
    union,
    unzip,
    without,
    xor
)

from .utilities import (
    after,
    aspath,
    atgetter,
    before,
    compose,
    constant,
    identity,
    ismatch,
    iteratee,
    noop,
    matches,
    pathgetter,
    pickgetter,
    random,
    retry
)
