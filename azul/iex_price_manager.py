import azul
import pyEX
import pandas as pd
import pytz


@azul.price_manager_registry.register('iex')
class IEXPriceManager(azul.BasePriceManager):

    def __init__(self):
        super().__init__()

    def _minute_dataframe_for_date(self, ticker: str, start_timestamp: pd.Timestamp) -> pd.DataFrame:

        # I monkey patched chartDF to get this working more than 1 date.
        df = pyEX.chartDF(ticker, timeframe='1d', date=start_timestamp)
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
            print("Skipping {0}, not all columns ({1}) received".format(ticker, str(df.columns)))
            #skipped_list.append(symbol)
            #continue
        df = self._fixna(df, ticker)
        df.index = df.index.tz_convert(None)

        # Re-arrange them
        df = df[self._cols]
        return df
