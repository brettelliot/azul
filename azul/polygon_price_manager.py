import requests
import pandas as pd
import numpy as np
import pathlib
import zipline as zl
import logbook
import datetime
import os
from azul import price_manager_registry, BasePriceManager

log = logbook.Logger('PolygonPriceManager')


@price_manager_registry.register('polygon')
class PolygonPriceManager(BasePriceManager):

    def __init__(self):
        super().__init__()
        api_key = os.getenv('AZUL_POLYGON_API_KEY')
        if not api_key or not isinstance(api_key, str):
            raise ValueError('The Polygon API key must be provided '
                             'through the environment variable '
                             'AZUL_POLYGON_API_KEY')
        self._api_key = api_key

    def _url(self, path):
        return 'https://api.polygon.io' + path

    # def get_stock_symbols(self, start_page=1, otc=False):
    #
    #     symbols = []
    #     still_getting_pages = True
    #     page = start_page
    #     isOTC = 'true' if otc else 'false'
    #
    #     while still_getting_pages:
    #
    #         params = {
    #             'apikey': self._api_key,
    #             'type': 'cs',
    #             'perpage': 50,
    #             'page': page,
    #             'isOTC': isOTC
    #         }
    #         url = self._url('/v1/meta/symbols')
    #         response = requests.get(url, params=params)
    #
    #         if response.status_code in[401, 404, 409]:
    #             log.error('Error getting symbols. Response code: {}'.format(response.status_code))
    #             still_getting_pages = False
    #             continue
    #         elif response.status_code != 200:
    #             still_getting_pages = False
    #             continue
    #
    #         try:
    #             json_dict = response.json()
    #             symbol_object_list = json_dict['symbols']
    #         except Exception as e:
    #             log.info('Could not read symbols.')
    #             log.info('Exception: {}', e)
    #             log.info('Status Code: {}'.format(response.status_code))
    #
    #         if not symbol_object_list:
    #             still_getting_pages = False
    #             continue
    #
    #         for symbol_object in symbol_object_list:
    #             symbols.append(symbol_object['symbol'])
    #
    #         log.info('Getting symbols page: {}'.format(page))
    #         page += 1
    #
    #     return symbols

    # def _list_date(self, ticker):
    #
    #     list_date = None
    #
    #     params = {
    #         'apikey': self._api_key,
    #     }
    #
    #     url = self._url('/v1/meta/symbols/{}/company'.format(ticker))
    #     response = requests.get(url, params=params)
    #
    #     if response.status_code != 200:
    #         log.info('Error getting company information for {}.'.format(ticker))
    #         log.info('Response status code: {}'.format(response.status_code))
    #         return list_date
    #
    #     try:
    #         json_dict = response.json()
    #         list_date = json_dict['listdate']
    #     except Exception as e:
    #         log.info('Did not get company list date information for: {}'.format(ticker))
    #
    #     if list_date is None:
    #         log.info('No list date provided for {}'.format(ticker))
    #     else:
    #         log.info('The list date for {} was {}'.format(ticker, list_date))
    #
    #     return list_date

    def _minute_dataframe_for_date(self, ticker: str, start_timestamp: pd.Timestamp) -> pd.DataFrame:

        # https://api.polygon.io/v1/historic/agg/minute/{symbol}?from=2000-01-03&to=2000-01-04&apikey=xxx

        end_timestamp = start_timestamp.replace(hour=23, minute=59)
        df = pd.DataFrame()

        params = {
            'apikey': self._api_key,
            # Pass in the time in ET
            #from': '2018-11-28 09:30:00',
            'from': start_timestamp,
            #'limit': 1440
            'to': end_timestamp
        }
        size = 'minute'
        url = self._url('/v1/historic/agg/{}/{}'.format(size, ticker))

        try:
            response = requests.get(url, params=params)
        except requests.exceptions.RequestException as e:
            log.error('Error getting historic agg {} data from polygon for: {} from: {} to: {}'.format(
                size, ticker, start_timestamp, end_timestamp))
            log.error('Exception: {}', e)
            return df

        if response.status_code != 200:
            log.error('Error getting historic agg {} data from polygon for: {} from: {} to: {}'.format(
                size, ticker, start_timestamp, end_timestamp))
            log.error('Response status code: {}', response.status_code)
            return df

        try:
            json_dict = response.json()
        except Exception as e:
            log.info('Could not read json data from historic agg response for: {} from: {} to: {}',
                     ticker, start_timestamp, end_timestamp)
            log.info('Exception: {}', e)
            log.info('Response code: {}', response.status_code)
            return df

        try:
            ticks = json_dict['ticks']
        except Exception as e:
            log.info('Could not read ticks data from historic agg response for: {} from: {} to: {}'.format(
                ticker, start_timestamp, end_timestamp))
            return df

        # polygon doesn't return in ascending order
        # Do not rely on df.sort_values() as this library
        # may be used with older
        df = pd.DataFrame(
            sorted(ticks, key=lambda t: t['t']),
            columns=('o', 'h', 'l', 'c', 'v', 't'),
        )

        # Give the colunms the names from the map.
        df.columns = [json_dict['map'][c] for c in df.columns]
        df.rename(columns={'timestamp': 'date'}, inplace=True)

        # Converting the index to a date
        size = json_dict['aggType']
        if size[0] == 'm':
            df.set_index('date', inplace=True)
            # astype is necessary to deal with empty result
            df.index = pd.to_datetime(
                df.index.astype('int64') * 1000000,
                utc=True,
                )

        df.sort_index(inplace=True)

        df = self._fixna(df, ticker)
        df.index = df.index.tz_convert(None)

        # Add (required?) columns for the CSVDIR bundle and re-arrange them
        df['dividend'] = 0.0
        df['split'] = 1.0
        df = df[self._cols]
        return df
