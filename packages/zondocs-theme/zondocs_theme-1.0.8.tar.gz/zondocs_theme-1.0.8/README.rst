======================================
New shiny Sphinx Theme for ZEIT ONLINE
======================================

Usage
-----

Install the package

.. code-block:: text

    $ pip install zondocs_theme

Then set ``html_theme = 'zondocs_theme'`` in your Sphinx ``conf.py``.

Features
--------

* Automatically uses the ZON logo.
* Adds an "edit this page" link to the sidebar. To customize how this link is
  created, you can set the following::

    html_theme_options = {
        'editme_link': (
            'https://github.com/zeitonline/{project}/edit/master/{page}')
    }

  (This is the default value, it supports two variables, ``project`` is taken
   directly from ``conf.py``, and ``page`` evaluates to
   ``path/to/current/page.suffix``)


Local testing
-------------

Run ``bin/build`` to build whl and use ``pip install zondocs_theme...whl`` to use it in your project.


Release process
---------------

`pipenv` is needed to run the release process.

Update the version in ``pyproject.toml``.

For a `test <https://test.pypi.org/project/zondocs-theme/>`_ release run

.. code-block:: text

    $ bin/release test

For a offical release run

.. code-block:: text

    $ bin/release prod
