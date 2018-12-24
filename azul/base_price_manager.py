import logbook
import pandas as pd
import zipline as zl
import datetime
import pathlib
import requests
import numpy as np

log = logbook.Logger('BasePriceManager')


class BasePriceManager(object):

    def __init__(self, calendar_name='NYSE'):
        self._calendar = zl.get_calendar(name=calendar_name)
        self._cols = ['open', 'high', 'low', 'close', 'volume', 'dividend', 'split']

    def get_price_data(self, symbols, output_dir, start_date_str, end_date_str):
        minute_dir_path = pathlib.Path(output_dir, 'minute')
        daily_dir_path = pathlib.Path(output_dir, 'daily')

        for ticker in symbols:
            self._download_and_process_data(
                ticker, start_date_str, end_date_str, minute_dir_path, daily_dir_path)

    def _download_and_process_data(self, ticker, start_date_str, end_date_str, minute_dir_path, daily_dir_path):
        df = self._minute_dataframe_for_dates(ticker, start_date_str, end_date_str)

        if df.empty:
            return

        df = self._check_sessions(df, ticker, frequency='minute')
        pathlib.Path(minute_dir_path).mkdir(parents=True, exist_ok=True)
        filename = pathlib.Path(minute_dir_path, ticker + '.csv')
        df.to_csv(filename)

        daily_df = self._resample_minute_data_to_daily_data(df)
        daily_df = self._check_sessions(daily_df, ticker, frequency='daily')
        pathlib.Path(daily_dir_path).mkdir(parents=True, exist_ok=True)
        filename = pathlib.Path(daily_dir_path, ticker + '.csv')
        daily_df.to_csv(filename)

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

    def _validated_start_and_end_dates(self, start_date_str, end_date_str):
        if start_date_str is None:
            start_date_str = datetime.datetime.today().strftime('%Y-%m-%d')
        if end_date_str is None:
            end_date_str = datetime.datetime.today().strftime('%Y-%m-%d')
        return start_date_str, end_date_str

    def _minute_dataframe_for_dates(self, ticker, start_date_str, end_date_str):

        start_date_str, end_date_str = self._validated_start_and_end_dates(start_date_str, end_date_str)

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
        raise NotImplementedError

    def _minute_dataframe_for_date(self, ticker, start_timestamp):
        raise NotImplementedError

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
