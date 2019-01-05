import unittest
from click.testing import CliRunner
import azul
import os
import pathlib
import pandas as pd
import shutil
import datetime
from tests.mock_price_manager import MockPriceManager
import tempfile
from datetime import datetime, timedelta


class TestDownloadCommand(unittest.TestCase):

    def setUp(self):
        # Set start date a few days before today
        self.start_date_str = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')

    def delete_home_dir_test_data_source(self):
        # The tests create a test dir which should be removed before and after the tests run.
        self.home_dir_test_data_source = pathlib.Path.home() / '.azul/mock_price_manager'

        try:
            shutil.rmtree(str(self.home_dir_test_data_source))
        except FileNotFoundError:
            pass
        self.assertFalse(pathlib.Path(self.home_dir_test_data_source).exists())

    @unittest.skip
    def test_download_sp500(self):

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(azul.cli, [
                '--symbol-source', 'sp500_wikipedia',
                '--data-source', 'polygon',
                '--start', self.start_date_str,
                'download'
            ])
            self.assertEqual(0, result.exit_code)

    def test_download_faang(self):

        # Given a directory for the data to be downloaded.
        with tempfile.TemporaryDirectory() as output_dir_name:
            output_dir_path = pathlib.Path(output_dir_name)

            # When the azul download command is run
            runner = CliRunner()
            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'mock_price_manager',
                '--start', self.start_date_str,
                '--output-dir', output_dir_name
            ])

            self.assertEqual(0, result.exit_code)
            expected = pathlib.Path(output_dir_path, 'minute')
            self.assertTrue(pathlib.Path(expected).exists())
            expected = pathlib.Path(output_dir_path, 'daily')
            self.assertTrue(pathlib.Path(expected).exists())

    def test_download_faang_iex(self):

        # Given a directory for the data to be downloaded.
        with tempfile.TemporaryDirectory() as output_dir_name:
            output_dir_path = pathlib.Path(output_dir_name)

            # When the azul download command is run
            runner = CliRunner()
            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'iex',
                '--start', self.start_date_str,
                '--output-dir', output_dir_name
            ])

            self.assertEqual(0, result.exit_code)
            expected = pathlib.Path(output_dir_path, 'minute')
            self.assertTrue(pathlib.Path(expected).exists())
            expected = pathlib.Path(output_dir_path, 'daily')
            self.assertTrue(pathlib.Path(expected).exists())

    def test_writes_data_to_home_directory_when_no_output_dir_is_specified(self):
        #  Scenario 1: No output_dir was specified:
        #  Create a default data dir in ~/.azul

        # Given a home dir without a test data source dir
        self.delete_home_dir_test_data_source()

        # When get_price_date is called with no output_dir specified
        runner = CliRunner()
        result = runner.invoke(azul.cli, [
            'download',
            '--symbol-source', 'faang',
            '--data-source', 'mock_price_manager',
            '--start', self.start_date_str
        ])

        # Then there will be data files in the home dir under the data source.
        self.assertEqual(0, result.exit_code)
        expected = self.home_dir_test_data_source
        self.assertTrue(pathlib.Path(expected).exists())
        expected = pathlib.Path(self.home_dir_test_data_source, 'minute')
        self.assertTrue(pathlib.Path(expected).exists())
        expected = pathlib.Path(self.home_dir_test_data_source, 'daily')
        self.assertTrue(pathlib.Path(expected).exists())

        # Delete the test data dir.
        self.delete_home_dir_test_data_source()

    def test_stops_trying_to_download_data_when_no_data_is_returned(self):

        # Given a place to put data
        with tempfile.TemporaryDirectory() as output_dir_name:
            output_dir_path = pathlib.Path(output_dir_name)

            # Sanity check we don't have daily and minute data.
            minute_path = pathlib.Path(output_dir_name, 'minute')
            self.assertFalse(pathlib.Path(minute_path).exists())
            daily_path = pathlib.Path(output_dir_name, 'daily')
            self.assertFalse(pathlib.Path(daily_path).exists())

            # When price data is retrieved for the last two months (from a source that only has data for the
            # last 35 days
            symbol_source = 'faang'
            data_source = 'mock_price_manager'
            start_date = datetime.now() - timedelta(days=60)
            end_date = datetime.now() - timedelta(days=0)
            azul.get_price_data(symbol_source, data_source, output_dir_path, start_date, end_date)

            # Then we have minute and daily data
            minute_path = pathlib.Path(output_dir_name, 'minute')
            self.assertTrue(pathlib.Path(minute_path).exists())
            daily_path = pathlib.Path(output_dir_name, 'daily')
            self.assertTrue(pathlib.Path(daily_path).exists())

            # And there is data from 35 days ago and more recently.
            aapl_daily_path = pathlib.Path(daily_path, 'aapl.csv')
            self.assertTrue(pathlib.Path(aapl_daily_path).exists())
            df = pd.read_csv(aapl_daily_path, parse_dates=True, index_col='date')
            actual_dates = df.index
            data_start_date = datetime.now() - timedelta(days=35)
            expected_dates = pd.date_range(data_start_date, end_date).normalize()
            self.assertFalse(set(expected_dates).isdisjoint(actual_dates))

            # And don't have any data from over 35 days ago in the daily files.
            expected_dates = pd.date_range(start=start_date, end=data_start_date).normalize()
            self.assertTrue(set(expected_dates).isdisjoint(actual_dates))




