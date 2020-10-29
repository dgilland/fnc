fnc
***

|version| |build| |coveralls| |license|


Functional programming in Python with generators and other utilities.


Links
=====

- Project: https://github.com/dgilland/fnc
- Documentation: https://fnc.readthedocs.io
- PyPI: https://pypi.python.org/pypi/fnc/
- Github Actions: https://github.com/dgilland/fnc/actions


Features
========

- Functional-style methods that work with and return generators.
- Shorthand-style iteratees (callbacks) to easily filter and map data.
- String object-path support for references nested data structures.
- 100% test coverage.
- Python 3.6+


Quickstart
==========

Install using pip:


::

    pip3 install fnc


Import the main module:

.. code-block:: python

    import fnc


Start working with data:

.. code-block:: python

    users = [
        {'id': 1, 'name': 'Jack', 'email': 'jack@example.org', 'active': True},
        {'id': 2, 'name': 'Max', 'email': 'max@example.com', 'active': True},
        {'id': 3, 'name': 'Allison', 'email': 'allison@example.org', 'active': False},
        {'id': 4, 'name': 'David', 'email': 'david@example.net', 'active': False}
    ]


Filter active users:

.. code-block:: python

    # Uses "matches" shorthand iteratee: dictionary
    active_users = fnc.filter({'active': True}, users)
    # <filter object at 0x7fa85940ec88>

    active_uesrs = list(active_users)
    # [{'name': 'Jack', 'email': 'jack@example.org', 'active': True},
    #  {'name': 'Max', 'email': 'max@example.com', 'active': True}]


Get a list of email addresses:

.. code-block:: python

    # Uses "pathgetter" shorthand iteratee: string
    emails = fnc.map('email', users)
    # <map object at 0x7fa8577d52e8>

    emails = list(emails)
    # ['jack@example.org', 'max@example.com', 'allison@example.org', 'david@example.net']


Create a ``dict`` of users keyed by ``'id'``:

.. code-block:: python

    # Uses "pathgetter" shorthand iteratee: string
    users_by_id = fnc.keyby('id', users)
    # {1: {'id': 1, 'name': 'Jack', 'email': 'jack@example.org', 'active': True},
    #  2: {'id': 2, 'name': 'Max', 'email': 'max@example.com', 'active': True},
    #  3: {'id': 3, 'name': 'Allison', 'email': 'allison@example.org', 'active': False},
    #  4: {'id': 4, 'name': 'David', 'email': 'david@example.net', 'active': False}}


Select only ``'id'`` and ``'email'`` fields and return as dictionaries:

.. code-block:: python

    # Uses "pickgetter" shorthand iteratee: set
    user_emails = list(fnc.map({'id', 'email'}, users))
    # [{'email': 'jack@example.org', 'id': 1},
    #  {'email': 'max@example.com', 'id': 2},
    #  {'email': 'allison@example.org', 'id': 3},
    #  {'email': 'david@example.net', 'id': 4}]


Select only ``'id'`` and ``'email'`` fields and return as tuples:

.. code-block:: python

    # Uses "atgetter" shorthand iteratee: tuple
    user_emails = list(fnc.map(('id', 'email'), users))
    # [(1, 'jack@example.org'),
    #  (2, 'max@example.com'),
    #  (3, 'allison@example.org'),
    #  (4, 'david@example.net')]


Access nested data structures using object-path notation:

.. code-block:: python

    fnc.get('a.b.c[1][0].d', {'a': {'b': {'c': [None, [{'d': 100}]]}}})
    # 100

    # Same result but using a path list instead of a string.
    fnc.get(['a', 'b', 'c', 1, 0, 'd'], {'a': {'b': {'c': [None, [{'d': 100}]]}}})
    # 100


Compose multiple functions into a generator pipeline:

.. code-block:: python

    from functools import partial

    filter_active = partial(fnc.filter, {'active': True})
    get_emails = partial(fnc.map, 'email')
    get_email_domains = partial(fnc.map, lambda email: email.split('@')[1])

    get_active_email_domains = fnc.compose(
        filter_active,
        get_emails,
        get_email_domains,
        set,
    )

    email_domains = get_active_email_domains(users)
    # {'example.com', 'example.org'}


Or do the same thing except using a terser "partial" shorthand:

.. code-block:: python

    get_active_email_domains = fnc.compose(
        (fnc.filter, {'active': True}),
        (fnc.map, 'email'),
        (fnc.map, lambda email: email.split('@')[1]),
        set,
    )

    email_domains = get_active_email_domains(users)
    # {'example.com', 'example.org'}


For more details and examples, please see the full documentation at https://fnc.readthedocs.io.


.. |version| image:: https://img.shields.io/pypi/v/fnc.svg?style=flat-square
    :target: https://pypi.python.org/pypi/fnc/

.. |build| image:: https://img.shields.io/github/workflow/status/dgilland/fnc/Main/master?style=flat-square
    :target: https://github.com/dgilland/fnc/actions

.. |coveralls| image:: https://img.shields.io/coveralls/dgilland/fnc/master.svg?style=flat-square
    :target: https://coveralls.io/r/dgilland/fnc

.. |license| image:: https://img.shields.io/pypi/l/fnc.svg?style=flat-square
    :target: https://pypi.python.org/pypi/fnc/
