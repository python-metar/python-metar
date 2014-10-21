.. python-metar documentation master file, created by
   sphinx-quickstart on Mon Oct 13 16:25:45 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

python-metar's documentation
========================================

.. image:: https://travis-ci.org/phobson/python-metar.svg?branch=master
    :target: https://travis-ci.org/phobson/python-metar
    :alt: Build Status

.. image:: https://coveralls.io/repos/phobson/python-metar/badge.png?branch=master
    :target: https://coveralls.io/r/phobson/python-metar?branch=master
    :alt: Test Coverage
    
.. image:: https://readthedocs.org/projects/python-metar/badge/?version=latest
    :target: https://readthedocs.org/projects/python-metar/?badge=latest
    :alt: Documentation Status


``python-metar`` is a library suited to parsing weather data in the METAR
format. METAR is kind of a mess and not very human-readable. Hopefully
this makes things a bit easier. What appears to be an official spec on the
format can be found here_.

.. _here: http://www.ncdc.noaa.gov/oa/wdc/metar/

Basic History
-------------

`Tom Pollard <https://github.com/tomp/python-metar>`_
originally wrote ``python-metar`` to parse weather hourly
reports as they were posted to the web. That basic functionality still
exists in this fork. Building on top of his original work, this fork aims
to provide convenient classes methods and to download data in bulk from
various sources, store in them nice
`data structures <http://pandas.pydata.org/>`_, and easily make usefule
visualizations of that data.

You can download my fork of the repoository from Github_.

.. _Github: https://github.com/phobson/python-metar

Dependencies
------------
* Python 2.7 or 3.3 (might work on 3.4)
* six for Python 2.7, 3.3 interoperability
* pip for installation
* recent versions of pandas, matplotlib
* requests for hitting the NOAA web API
* ipython-notebook for running examples (optional)
* nose and coverage for testing (both optional)
* sphinx to build the documentation (optional)

If you're using `environments <http://conda.pydata.org/docs/intro.html>`_
managed through ``conda`` (recommended), this will
get you started: ::

    conda create --name=metar python=3.3 ipython-notebook pip nose pandas matplotlib six requests coverage

Followed by: ::

    source activate metar # (omit "source" on Windows)

Installation
------------

* Activate your ``conda`` environment;
* Clone my fork from Github;
* Change to that resulting directory;
* Install via pip; and
* Back out of that directory to use

::

    source activate metar # (omit "source" on Windows)
    git clone https://github.com/phobson/python-metar
    cd python-metar
    pip install .
    cd ../..

Testing
-------

Tests are run via ``nose``. Run them all with: ::

    source activate metar # (omit "source" on Windows)
    python -c "import metar; metar.test()"

You can get fancy with: ::

    python -c "import metar; metar.test(verbose=True, packageinfo=True, coverage=True)"

Contents:
---------

.. toctree::
   :maxdepth: 2

   Primary API <metar/station>
   Data visualization <metar/graphics>
   Data export/formats <metar/exporters>
   Low-level API <metar/metar>
   Datatypes <metar/datatypes>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

