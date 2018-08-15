Versioning
==========

This project follows `Semantic Versioning`_ with the following caveats:

- Only the public API (i.e. the objects imported into the fnc module) will maintain backwards compatibility between MINOR version bumps.
- Objects within any other parts of the library are not guaranteed to not break between MINOR version bumps.

With that in mind, it is recommended to only use or import objects from the main module, fnc.


.. _Semantic Versioning: http://semver.org/
