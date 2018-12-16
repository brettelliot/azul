====
Azul
====
``azul`` is a command line tool and python package for downloading historical price data as CSV's ready for use in a zipline bundle.

For more documentation, please see http://azul.readthedocs.io.

Installation
------------
``azul`` can be easily installed with pip::

    $ pip install azul

Command line usage
------------------
To get the last 30 days of minute data for SPY from IEX::

    $ azul download --symbol-list SPY

This downloads the default range (last 30 days) from the default source (IEX) and puts it in the default data directory:``~/.azul/iex/minute/``. It also downsamples the minute data and creates daily bars from it in ``~/.azul/iex/daily/``.

Ingesting the CSV data into zipline
-----------------------------------
Once data has been downloaded, we can then turn it into a bundle that zipline can read. We do that with the zipline bundle tool and the ingest command::

    $ CSVDIR=~/.azul/iex/ zipline ingest -b my-azul-iex-bundle`

Package Usage
-------------
``azul`` can be used as a Python package very simply. Here's how you download historical minute and daily bars:
.. code-block:: python

    import azul
    symbols = ['SPY']
    source = 'IEX'
    azul.download(symbols, source)

This gets the last 30 days of minute data for SPY from IEX and puts it in the default data directory for IEX: ``~/.azul/iex/minute/SPY.csv``. It then downsamples that data and creates daily bars from it in ``~/.azul/iex/daily/SPY.csv``.


