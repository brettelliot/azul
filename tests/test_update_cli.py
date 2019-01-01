import unittest
from tests.mock_price_manager import MockPriceManager
from datetime import datetime, timedelta
import pathlib
import shutil
import azul
from click.testing import CliRunner
import tempfile
import pandas as pd


class TestUpdateCommand(unittest.TestCase):

    def setUp(self):
        # Set start date 30 days before today
        pass

    @unittest.skip
    def test_update_existing_data_dir(self):
        # Given an existing data dir
        with tempfile.TemporaryDirectory() as output_dir_name:
            output_dir_path = pathlib.Path(output_dir_name)

            # With data up to a week ago
            symbol_source = 'faang'
            data_source = 'mock_price_manager'
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now() - timedelta(days=7)
            azul.get_price_data(symbol_source, data_source, output_dir_path, start_date, end_date)

            # Sanity check we have daily and minute data.
            minute_path = pathlib.Path(output_dir_name, 'minute')
            self.assertTrue(pathlib.Path(minute_path).exists())
            daily_path = pathlib.Path(output_dir_name, 'daily')
            self.assertTrue(pathlib.Path(daily_path).exists())

            # Sanity check that we don't have any data from the last 7 days in the daily files.
            aapl_daily_path = pathlib.Path(daily_path, 'aapl.csv')
            self.assertTrue(pathlib.Path(aapl_daily_path).exists())
            df = pd.read_csv(aapl_daily_path, parse_dates=True, index_col='date')
            dr = df.index
            out_side_dates = pd.date_range(end_date, datetime.now())
            self.assertTrue(out_side_dates not in dr)

            # When updated
            azul.update_price_data(data_source=data_source, output_dir_path=output_dir_path)

            # Then there is date from the last week
            # Sanity check we have daily and minute data.
            self.assertTrue(pathlib.Path(minute_path).exists())
            self.assertTrue(pathlib.Path(daily_path).exists())

            # Check that we have the new data from the last 7 days in the daily files.
            self.assertTrue(pathlib.Path(aapl_daily_path).exists())
            df = pd.read_csv(aapl_daily_path, parse_dates=True, index_col='date')
            actual_dates = df.index
            expected_dates = pd.date_range(end_date, datetime.now()).normalize()
            self.assertFalse(set(expected_dates).isdisjoint(actual_dates))

