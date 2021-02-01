from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
import types


number_types = (int, float, Decimal)

Sentinel = object()


class _Unset(object):
    """
    Represents an unset value.

    Used to differentiate between an explicit ``None`` and an unset value.
    """

    def __bool__(self):  # pragma: no cover
        return False


UNSET = _Unset()


class Container(object):
    """
    A "seen" container for keeping track of elements of a sequence that have been encountered
    before.

    It is optimized to work with both hashable and unhashable values by storing hashable items in a
    ``set`` and unhashable items in a ``list`` and then checking both containers for existence.
    """

    def __init__(self, values=None):
        self.hashable = set()
        self.unhashable = []

        if values is not None:
            self.extend(values)

    def __contains__(self, value):
        try:
            return value in self.hashable
        except TypeError:
            return value in self.unhashable

    def __len__(self):  # pragma: no cover
        return len(self.hashable) + len(self.unhashable)

    def add(self, value):
        if value in self:
            return

        try:
            self.hashable.add(value)
        except TypeError:
            self.unhashable.append(value)

    def extend(self, values):
        for value in values:
            self.add(value)


def iscollection(value):
    """Return whether `value` is iterable but not string or bytes."""
    return isinstance(value, Iterable) and not isinstance(value, (str, bytes))


def isgenerator(value):
    """
    Return whether `value` is a generator or generator-like.

    The purpose being to determine whether `value` will be exhausted if it is iterated over.
    """
    return isinstance(value, types.GeneratorType) or (
        hasattr(value, "__iter__")
        and hasattr(value, "__next__")
        and not hasattr(value, "__getitem__")
    )


def iterate(mapping):
    """
    Attempt to iterate over `mapping` such that key-values pairs are yielded per iteration. For
    dictionaries and other mappings, this would be the keys and values. For lists and other
    sequences, this would be the indexes and values. For other non- standard object types, some
    duck-typing will be used:

    - If `mapping` has callable ``mapping.items()`` attribute, it will be used.
    - If `mapping` has callable ``mapping.keys()`` and ``__getitem__`` attributes, then
      ``(key, mapping[key])`` will be used.
    - Otherwise, `iter(mapping)` will be returned.
    """
    if isinstance(mapping, Mapping) or callable(getattr(mapping, "items", None)):
        return mapping.items()

    if isinstance(mapping, Sequence):
        return enumerate(mapping)

    if callable(getattr(mapping, "keys", None)) and hasattr(mapping, "__getitem__"):
        return ((key, mapping[key]) for key in mapping.keys())

    return iter(mapping)
