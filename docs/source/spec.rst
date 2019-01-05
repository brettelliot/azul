============
Product Spec
============

Vision and Overview
-------------------
Azul exists to make it easy for hobbyist quants and algorithmic traders to get data into zipline for backtesting. Ideally, most users will interact with azul from the command line however, a python package is included for programattic use cases too.

Success Metrics
---------------
Azul will be successful when a quant can run a zipline backtest using a bundle built from azul data containing 5 years of minute and daily level data for all the S&P500 stocks.

Use Cases and Prototypes
------------------------
There are plenty of ways to use ``azul``. Here are a few.

Minute and daily data for FAANG stocks from IEX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Say the algo trader wants minute and daily data for the FAANG stocks (Facebook, Amazon, Apple, Netflix, and Google)  so she can backtest in zipline.

This gets the FAANG symbols from the FaangSymbolFetcher (a trivial example), pulls minute level data from IEX (the default data source), covering the trailing 30 calendar days (the default), generates daily bars for each day and stores the results in the default output dir (``~/.azul/<data-source>``)::

    $ azul download --symbol-source faang --data-source iex --output-dir ~/.azul/iex

Because of the default value the above command can be shortened to::

    $ azul download

Updating previously downloaded data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now a few days go by and the algo trader wants to get the newest price data for the stocks she downloaded earlier in the week. To do that, she uses the ``update`` command::

    $ azul update --data-source iex --output-dir ~/.azul/iex

Because of the default values the above command can be shortened to::

    $ azul update

S&P 500 from polygon
~~~~~~~~~~~~~~~~~~~~
A algo trader wants minute and daily data for the S&P500 stocks for the last 5 years so she can backtest in zipline.

This gets the S&P500 symbols from wikipedia, pulls minute level data from polygon for the last 5 years, generates daily bars for each day and stores the results in ``~/.azul/polygon/minute`` and ``~/.azul/polygon/daily``::

    $ azul download --symbol-source sp500_wikipedia --data-source polygon --start 2018-01-01

Then to ingest this data into zipline use the ``zipline ingest`` command::

    $ CSVDIR=~/.azul/polygon/ zipline ingest -b my-azul-polygon-bundle`

A few days, weeks, or months go by and she wants to update her data. This will look at the symbols in ``~/.azul/polygon``, find the last bar, and the download everything between the last bar and now::

    $ azul update --data-source polygon

Other use cases
~~~~~~~~~~~~~~~
Get minute and daily data for some stocks on the london exchange using a different trading calendar::

    $ azul download --symbol-source london --trading-calendar XLON


Acceptance Criteria
-------------------
Using the command line interface a quant can:

* Obtain the current list of symbols in the S&P500.
* Configure azul to pull historical stock price data from IEX.
* Configure azul to pull historical stock price data from Polygon.
* Configure the start and end dates for the data download.
* Configure the data directory for downloading and updating data.
* Configure azul with a trading calendar that knows all available bars to download data for.
* Download historical minute level price data for a symbol for all bars in a trading calendar.
* Update a previously existing data directory with any new data that is available.

Future work
~~~~~~~~~~~
* Obtain the list of symbols in the S&P500 for a specific date.
* Obtain the list of symbols in the S&P500 for a specific date range.
