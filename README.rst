====
Azul
====
``azul`` is a python package for downloading historical price data as CSV's ready for use in a zipline bundle.

For more documentation, please see http://azul.readthedocs.io.

Installation
------------
``azul`` can be easily installed with pip::

    $ pip install azul

Usage
-----
``azul`` is really simple to use. Below you'll find the basics.

Download historical minute and daily bars
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the historical minute and daily bars simply import ``azul`` and call ``get_bars()``:

.. code-block:: python

    import azul

    azul.get_bars('SPY')

This gets the last 30 days of minute data for SPY from IEX and puts it in ``~/.azul/iex/minute/SPY.csv``. It then downsamples that data and creates daily bars from it in ``~/.azul/iex/daily/SPY.csv``.

Ingesting the CSV data into zipline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To get this data into zipline we have to first ingest it into a bundle. We do that with the zipline bundle tool::

    $ CSVDIR=~/.azul/iex/ zipline ingest -b my-azul-iex-bundle`

