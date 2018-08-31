Changelog
=========


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
