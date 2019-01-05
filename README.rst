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
``azul`` was designed to be a command line tool as well as a toolkit. Here are some examples showing how to get data using the command line. To get help from the command line you can see what sub commands are available with this::

    $ azul --help

One sub command is ``download``. You can see its arguments like this::

    $ azul download --help

Minute and daily data for FAANG stocks from IEX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Say you want to download minute and daily data for the FAANG stocks (Facebook, Amazon, Apple, Netflix, and Google). This gets the FAANG symbols, pulls minute level data from IEX (the default data source) covering the last 30 calendar days (the default date range for IEX), generates daily bars for each day, and stores the results in the default output directory for IEX(``~/.azul/iex``)::

    $ azul download --symbol-source faang

The above command took advanage of some of the command line default arguements but can be re-written like this to be explict::

    $ azul download  --symbol-source faang --data-source iex --output-dir ~/.azul/iex

This downloads the last 30 days from IEX and puts it in:``~/.azul/iex/minute/``. It also downsamples the minute data and creates daily bars from, storing those in: ``~/.azul/iex/daily/``.

Minute and daily data for the S&P 500 from polygon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now say you want minute and daily data for the S&P500 stocks for the last 5 years. Polygon requires an API key which you can get from them. Once you do, just set the ``AZUL_POLYGON_API_KEY`` environment variable in a script or on the command line like this::

    $ export AZUL_POLYGON_API_KEY=you_polygon_key_id

Then use ``azul`` to get the data and store it in a way that can be processed by zipline. This gets the S&P500 symbols from wikipedia, pulls minute level data from polygon for the last 5 years, generates daily bars for each day and stores the results in ``~/.azul/polygon/minute`` and ``~/.azul/polygon/daily``::

    $ azul download --symbol-source sp500_wikipedia --data-source polygon --start 2018-01-01

Ingesting the CSV data into zipline
-----------------------------------
Once data has been downloaded, we can then turn it into a bundle that zipline can read. We do that with the zipline bundle tool and the ingest command. Here's how you might ingest the IEX data::

    $ CSVDIR=~/.azul/iex/ zipline ingest -b my-azul-iex-bundle`

And here's how you might ingest the Polygon data::

    $ CSVDIR=~/.azul/polygon/ zipline ingest -b my-azul-polygon-bundle`

