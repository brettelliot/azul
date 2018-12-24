import unittest
from click.testing import CliRunner
import azul
import os
import pathlib
import pandas as pd
import pytz


@azul.price_manager_registry.register('mock_price_manager')
class MockPriceManager(azul.BasePriceManager):

    def __init__(self):
        super().__init__()

    def _list_date(self, ticker):
        return None

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


class TestWriteSymbols(unittest.TestCase):

    @unittest.skip
    def test_download_sp500(self):

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(azul.cli, [
                '--symbol-source', 'sp500_wikipedia',
                '--data-source', 'polygon',
                '--start', '2014-01-01',
                'download'
            ])
            self.assertEqual(0, result.exit_code)

    def test_download_faang(self):

        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir('test_data_dir')

            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'mock_price_manager',
                '--start', '2018-12-20',
                '--output-dir', 'test_data_dir'
            ])

            self.assertEqual(0, result.exit_code)
            expected = 'test_data_dir/minute'
            self.assertTrue(pathlib.Path(expected).exists())
            expected = 'test_data_dir/daily'
            self.assertTrue(pathlib.Path(expected).exists())

