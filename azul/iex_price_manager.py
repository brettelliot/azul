import azul
import pyEX
import pandas as pd
import pytz
from datetime import datetime, timedelta
from typing import Tuple
import logbook


log = logbook.Logger('IEXPriceManager')


@azul.price_manager_registry.register('iex')
class IEXPriceManager(azul.BasePriceManager):

    def __init__(self):
        super().__init__()

    def _validated_start_and_end_dates(
            self,
            start_date: datetime,
            end_date: datetime
    ) -> Tuple[datetime, datetime]:
        """
        Creates valid start and end dates. Ensures start date is no greater than 30 calendar days ago (IEX limitation).

        Args:
            start_date (datetime): The start date.
            end_date (datetime): The end date.

        Returns:
            start_date (datetime): The validated start date.
            end_date (datetime): The validated end date.

        """
        today = datetime.today()
        thirty_days_ago = today - timedelta(days=30)

        # Ensure the start (and end) date are not greater than 30 days ago (the limitation on minute data).
        if start_date is not None:
            if (today - start_date).days > 30:
                start_date = thirty_days_ago
                log.info('IEX start date can be at most 30 calendar days ago. Resetting to: %s' % start_date.date())

        if end_date is not None:
            if (today - end_date).days > 30:
                log.info('IEX end date can be at most 30 calendar days ago. Resetting to: %s' % end_date.date())
                end_date = today

        if start_date is None:
            start_date = thirty_days_ago

        if end_date is None:
            end_date = today

        # Sanity check the results.
        if start_date > end_date:
            temp_date = start_date
            start_date = end_date
            end_date = temp_date

        return start_date, end_date

    def _minute_dataframe_for_date(self, ticker: str, start_timestamp: pd.Timestamp) -> pd.DataFrame:
        ret_df = pd.DataFrame()

        df = pyEX.chartDF(ticker, timeframe='1d', date=start_timestamp)

        if df.empty:
            return ret_df

        df = df.reset_index()
        df['volume'] = df['volume'].astype('int')
        df['date'] = df['date'].astype('str')
        df['minute'] = df['minute'].astype('str')
        df['datet'] = df['date'] + ' ' + df['minute']
        df['dividend'] = 0.0
        df['split'] = 1.0
        df.drop(['date', 'minute', 'average', 'changeOverTime', 'close', 'high', 'label', 'low', 'marketAverage',
                 'marketChangeOverTime', 'marketNotional', 'marketNumberOfTrades', 'notional', 'numberOfTrades',
                 'open', 'volume'], axis=1, level=None, inplace=True, errors='ignore')
        df.rename(columns={'datet': 'date', 'marketClose': 'close', 'marketHigh': 'high', 'marketLow': 'low',
                           'marketOpen': 'open', 'marketVolume': 'volume'}, inplace=True)
        df.date = pd.to_datetime(df.date, errors='coerce', utc=False, infer_datetime_format=True)
        df = df[~df.date.isnull()]
        df.set_index('date', drop=True, append=False, inplace=True, verify_integrity=True)

        utc = pytz.utc
        nytz = pytz.timezone('US/Eastern')
        df = df.tz_localize(nytz, axis=0, level=None, copy=False, ambiguous='raise')
        df.index = df.index.tz_convert(utc)
        if not (pd.Series(['close', 'high', 'low', 'open']).isin(df.columns).all()):
            log.info("Skipping {0} for {1}, not all columns ({2}) received".format(
                ticker, start_timestamp.date(), str(df.columns)))
            return ret_df

        df = self._fixna(df, ticker)
        df.index = df.index.tz_convert(None)

        # Re-arrange them
        ret_df = df[self._cols]
        return ret_df
