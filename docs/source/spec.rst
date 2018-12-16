==========
SPEC: Azul
==========

Vision and Overview
-------------------
Azul exists to make it easy for hobbyist quants and algorithmic traders to get data into zipline for backtesting. Ideally, most users will interact with azul from the command line however, a python package is included for programattic use cases too.

Success Metrics
---------------
Azul will be successful when a quant can run a zipline backtest using a bundle built from azul data containing 5 years of minute and daily level data for all the S&P500 stocks.

Use Cases and Prototypes
------------------------
Get the current list of symbols in the S&P500 and save them in a file called sp500.txt::

    $ azul get_symbols --source sp500

Get minute and daily data for the S&P500 for the last 30 days from IEX::

    $ azul download --symbol-list sp500.txt

Get minute and daily data for the S&P500 for the last 30 days from IEX and put it someplace special::

    $ azul download --symbol-list sp500.txt --data-dir ./my_iex_data

Get minute and daily data for the S&P500 for the last 30 days from polygon::

    $ azul download --symbol-list sp500.txt --source polygon

Get minute and daily data for the S&P500 from polygon starting at a specific date::

    $ azul download --symbol-list sp500.txt --source polygon --start 2018-11-01

Get minute and daily data for the S&P500 from polygon starting at a specific date range::

    $ azul download --symbol-list sp500.txt --source polygon --start 2018-11-01 --end 2018-11-30

Get minute and daily data for some stocks on the london exchange::

    $ azul download --symbol-list london.txt --trading-calendar XLON

Update previously downloaded data with anything new that is available::

    $ azul update --source polygon

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
