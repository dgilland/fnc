Changelog
=========


v0.5.3 (2021-10-14)
-------------------

- Minor performance optimization in ``pick``.


v0.5.2 (2020-12-24)
-------------------

- Fix regression in ``v0.5.1`` that broke ``get/has`` for dictionaries and dot-delimited keys that reference integer dict-keys.


v0.5.1 (2020-12-14)
-------------------

- Fix bug in ``get/has`` that caused ``defaultdict`` objects to get populated on key access.


v0.5.0 (2020-10-23)
-------------------

- Fix bug in ``intersection/intersectionby`` and ``difference/differenceby`` where incorrect results could be returned when generators passed in as the sequences to compare with.
- Add support for Python 3.9.
- Drop support for Python <= 3.5.


v0.4.0 (2019-01-23)
-------------------

- Add functions:

  - ``differenceby``
  - ``duplicatesby``
  - ``intersectionby``
  - ``unionby``


v0.3.0 (2018-08-31)
-------------------

- compose: Introduce new "partial" shorthand where instead of passing a callable, a ``tuple`` can be given which will then be converted to a callable using ``functools.partial``. For example, instead of ``fnc.compose(partial(fnc.filter, {'active': True}), partial(fnc.map, 'email'))``, one can do ``fnc.compose((fnc.filter, {'active': True}), (fnc.map, 'email'))``.


v0.2.0 (2018-08-24)
-------------------

- Add functions:

  - ``negate``
  - ``over``
  - ``overall``
  - ``overany``

- Rename functions: (**breaking change**)

  - ``ismatch -> conforms``
  - ``matches -> conformance``

- Make ``conforms/conformance`` (formerly ``ismatch/matches``) accept callable dictionary values that act as predicates against comparison target. (**breaking change**)


v0.1.1 (2018-08-17)
-------------------

- pick: Don't return ``None`` for keys that don't exist in source object. Instead of ``fnc.pick(['a'], {}) == {'a': None}``, it's now ``fnc.pick(['a'], {}) == {}``.


v0.1.0 (2018-08-15)
-------------------

- First release.
