import requests
import pandas as pd
import numpy as np
import pathlib
import zipline as zl
import logbook
import datetime
import azul


pd.set_option('display.expand_frame_repr', False)
log = logbook.Logger('MinuteDownloader')

@azul.price_manager_registry.register('polygon')
class PolygonPriceManager(object):

    def __init__(self, calendar_name='NYSE', api_key=None):
        self._api_key = api_key
        self._calendar = zl.get_calendar(name=calendar_name)
        self._cols = ['open', 'high', 'low', 'close', 'volume', 'dividend', 'split']

    def _url(self, path):
        return 'https://api.polygon.io' + path

    def get_stock_symbols(self, start_page=1, otc=False):

        symbols = []
        still_getting_pages = True
        page = start_page
        isOTC = 'true' if otc else 'false'

        while still_getting_pages:

            params = {
                'apikey': self._api_key,
                'type': 'cs',
                'perpage': 50,
                'page': page,
                'isOTC': isOTC
            }
            url = self._url('/v1/meta/symbols')
            response = requests.get(url, params=params)

            if response.status_code in[401, 404, 409]:
                log.error('Error getting symbols. Response code: {}'.format(response.status_code))
                still_getting_pages = False
                continue
            elif response.status_code != 200:
                still_getting_pages = False
                continue

            try:
                json_dict = response.json()
                symbol_object_list = json_dict['symbols']
            except Exception as e:
                log.info('Could not read symbols.')
                log.info('Exception: {}', e)
                log.info('Status Code: {}'.format(response.status_code))

            if not symbol_object_list:
                still_getting_pages = False
                continue

            for symbol_object in symbol_object_list:
                symbols.append(symbol_object['symbol'])

            log.info('Getting symbols page: {}'.format(page))
            page += 1

        return symbols

    def download_and_process_data_from_polygon(self, ticker, start_date_str, end_date_str, minute_dir, daily_dir):
        df = self._minute_dataframe_for_dates(ticker, start_date_str, end_date_str)

        if df.empty:
            return

        df = self._check_sessions(df, ticker, frequency='minute')
        pathlib.Path(minute_dir).mkdir(parents=True, exist_ok=True)
        filename = minute_dir + '/' + ticker + '.csv'
        with open(filename, 'w') as f:
            df.to_csv(f)
            f.close()

        daily_df = self._resample_minute_data_to_daily_data(df)
        daily_df = self._check_sessions(daily_df, ticker, frequency='daily')
        pathlib.Path(daily_dir).mkdir(parents=True, exist_ok=True)
        filename = daily_dir + '/' + ticker + '.csv'
        with open(filename, 'w') as f:
            daily_df.to_csv(f)
            f.close()

    def _resample_minute_data_to_daily_data(self, df):
        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'dividend': 'last',
            'split': 'last'
        }

        if df.empty:
            daily_df = df
        else:
            daily_df = df.resample('D', closed='left', label='left').agg(ohlc_dict).dropna(how='any')

        # Resample mixes the columns so lets re-arrange them

        daily_df = daily_df[self._cols]
        return daily_df

    def _minute_dataframe_for_dates(self, ticker, start_date_str, end_date_str):

        combined_df = pd.DataFrame(columns=self._cols)
        combined_df.index.name = 'date'

        # Get the date the symbol was listed on the exchange.
        list_date_str = self._list_date(ticker)

        if list_date_str is not None:
            list_date_dt = datetime.datetime.strptime(list_date_str, '%Y-%m-%d')
            start_date_dt = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')

            # If the we are asking for data from before the stock was listed, then set the start date to the day
            # the stock was listed.
            if list_date_dt > start_date_dt:
                log.info('The symbol {} was not listed until: {}. Adjusting start time.', ticker, list_date_str)
                start_date_str = list_date_str

        # Build a list of the trading days from the dates passed in.
        session_dates = self._calendar.sessions_in_range(start_date_str, end_date_str)

        if session_dates.empty:
            log.info('The symbol {} did not trade between {} and {} ', ticker, start_date_str, end_date_str)
            return combined_df

        for timestamp in session_dates:
            date_str = timestamp.strftime('%Y-%m-%d')
            df = self._minute_dataframe_for_date(ticker, timestamp)
            if df.empty:
                # probably change this to info
                log.info('No minute data for {} on {}'.format(ticker, date_str))
            else:
                log.info('Retrieved minute data for {} on {}'.format(ticker, date_str))
            combined_df = pd.concat([combined_df, df])

        return combined_df

    def _list_date(self, ticker):

        list_date = None

        params = {
            'apikey': self._api_key,
        }

        url = self._url('/v1/meta/symbols/{}/company'.format(ticker))
        response = requests.get(url, params=params)

        if response.status_code != 200:
            log.info('Error getting company information for {}.'.format(ticker))
            log.info('Response status code: {}'.format(response.status_code))
            return list_date

        try:
            json_dict = response.json()
            list_date = json_dict['listdate']
        except Exception as e:
            log.info('Did not get company list date information for: {}'.format(ticker))

        if list_date is None:
            log.info('No list date provided for {}'.format(ticker))
        else:
            log.info('The list date for {} was {}'.format(ticker, list_date))

        return list_date

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

        response = requests.get(url, params=params)

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

    def _fixna(self, df, symbol):
        cols = ['close', 'high', 'low', 'open']
        df[cols] = df[cols].replace({0: np.nan})
        df[cols] = df[cols].replace({-1.0: np.nan})
        if df.isnull().sum().sum() > 0:
            # fixna_list.append(symbol)
            df['open'] = df['open'].bfill().ffill()
            df['close'] = df['close'].bfill().ffill()
            df.loc[df['low'].isnull(), 'low'] = df['open']
            df.loc[df['high'].isnull(), 'high'] = df['open']
            df.loc[df['close'].isnull(), 'close'] = df['open']
        return df

    def _check_sessions(self, df, ticker, frequency='daily'):

        # Remove any data that are outside of the trading sessions for the calendar.

        if df.empty:
            return df

        asset_first_day = df.index[0]
        asset_last_day = df.index[-1]
        sessions = self._calendar.sessions_in_range(asset_first_day, asset_last_day)
        asset_sessions = sessions[sessions.slice_indexer(asset_first_day, asset_last_day)]

        if frequency == 'minute':
            minutes_passed = len(df)
            asset_first_day = self._calendar.minute_to_session_label(asset_first_day, direction='next')
            asset_last_day = self._calendar.minute_to_session_label(asset_last_day, direction='previous')
            minutes_in_session = self._calendar.minutes_for_sessions_in_range(asset_first_day, asset_last_day)
            df = df[df.index.isin(minutes_in_session)]
            if (minutes_passed) > len(minutes_in_session):
                #print('Removed ' + str((minutes_passed) - len(minutes_in_session)) + ' minutes')
                pass
            elif minutes_passed < len(minutes_in_session):
                num_missing_sessions = len(minutes_in_session) - minutes_passed
                log.info('Missing sessions for {}'.format(ticker))
        elif frequency == 'daily' and len(df) != len(asset_sessions):
            missing_sessions = asset_sessions.difference(
                pd.to_datetime(np.array(df.index), unit='s', utc=True, )).tolist()
            extra_sessions = pd.to_datetime(np.array(df.index), unit='s', utc=True, ).difference(
                asset_sessions).tolist()
            if len(missing_sessions) > 0:
                #missing_sessions_list.append(symbol)
                #print('Adding ' + str(len(missing_sessions)) + ' sessions for ' + str(ticker))
                pass
            if len(extra_sessions) > 0:
                #extra_sessions_list.append(symbol)
                #print('Removing ' + str(len(extra_sessions)) + ' sessions for ' + str(symbol))
                pass
            for missing_session in missing_sessions:
                prev_date = self._calendar.previous_session_label(missing_session)
                row_to_copy = df[(df.index == prev_date)]
                row_to_copy_val = row_to_copy.values
                # from IPython import embed; embed()
                df.loc[missing_session] = row_to_copy_val[0]
                df.loc[missing_session].volume = 0
                # row = row_to_copy
                # table.append(row)

            for extra_session in extra_sessions:
                # delete stuff
                df.drop(extra_session)

        if frequency == 'minute':
            log.notice('Downloaded and processed {} minute bars for {}', len(df), ticker)
        else:
            log.notice('Downsampled {} daily bars for {}', len(df), ticker)

        return df