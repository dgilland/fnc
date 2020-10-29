Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:


Types of Contributions
----------------------

Report Bugs
+++++++++++

Report bugs at https://github.com/dgilland/fnc.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.


Fix Bugs
++++++++

Look through the GitHub issues for bugs. Anything tagged with "bug" is open to whoever wants to implement it.


Implement Features
++++++++++++++++++

Look through the GitHub issues for features. Anything tagged with "enhancement" or "help wanted" is open to whoever wants to implement it.


Write Documentation
+++++++++++++++++++

fnc could always use more documentation, whether as part of the official fnc docs, in docstrings, or even on the web in blog posts, articles, and such.


Submit Feedback
+++++++++++++++

The best way to send feedback is to file an issue at https://github.com/dgilland/fnc.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome :)


Get Started!
------------

Ready to contribute? Here's how to set up ``fnc`` for local development.

1. Fork the ``fnc`` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_username_here/fnc.git

3. Install Python dependencies into a virtualenv::

    $ cd fnc
    $ pip install -r requirements.txt

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. Autoformat code::

    $ inv fmt

6. When you're done making changes, check that your changes pass all unit tests by testing with ``tox`` across all supported Python versions::

    $ tox

7. Add yourself to ``AUTHORS.rst``.

8. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "<Detailed description of your changes>"
    $ git push origin name-of-your-bugfix-or-feature-branch

9. Submit a pull request through GitHub.


Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. The pull request should work for all versions Python that this project supports.
