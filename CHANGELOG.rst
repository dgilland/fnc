Changelog
=========


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
