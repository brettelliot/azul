from azul import price_manager_registry, BasePriceManager
import pandas as pd


@price_manager_registry.register('mock_price_manager')
class MockPriceManager(BasePriceManager):

    def __init__(self):
        super().__init__()

    def _minute_dataframe_for_date(self, ticker, start_timestamp):
        end_timestamp = start_timestamp.replace(hour=23, minute=59)

        session_minutes = pd.date_range(
            start_timestamp, end_timestamp, freq='min'
        )

        # Create a dataframe with a row for every minute the days session.
        df = pd.DataFrame({'date': session_minutes})
        df = df.set_index('date')

        # Add columns with fake data for each row.
        df['open'] = 10.0
        df['high'] = 15.0
        df['low'] = 5.0
        df['close'] = 13.0
        df['volume'] = 100000
        df['dividend'] = 0.0
        df['split'] = 1.0
        df = df[self._cols]

        return df
