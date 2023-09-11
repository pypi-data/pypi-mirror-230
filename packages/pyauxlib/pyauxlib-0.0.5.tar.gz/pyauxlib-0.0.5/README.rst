========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/pyauxlib/badge/?style=flat
    :target: https://pyauxlib.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/psolsfer/pyauxlib/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/psolsfer/pyauxlib/actions

.. |version| image:: https://img.shields.io/pypi/v/pyauxlib.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/pyauxlib

.. |wheel| image:: https://img.shields.io/pypi/wheel/pyauxlib.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/pyauxlib

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/pyauxlib.svg
    :alt: Supported versions
    :target: https://pypi.org/project/pyauxlib

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/pyauxlib.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/pyauxlib

.. |commits-since| image:: https://img.shields.io/github/commits-since/psolsfer/pyauxlib/v0.0.5.svg
    :alt: Commits since latest release
    :target: https://github.com/psolsfer/pyauxlib/compare/v0.0.5...main



.. end-badges

Auxiliary library for python.

* Free software: BSD 3-Clause License

Installation
============

::

    pip install pyauxlib

You can also install the in-development version with::

    pip install https://github.com/psolsfer/pyauxlib/archive/main.zip


Documentation
=============


https://pyauxlib.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
