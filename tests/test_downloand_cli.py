import unittest
from click.testing import CliRunner
import azul
import os
import pathlib
import pandas as pd
import shutil
import datetime


@azul.price_manager_registry.register('mock_price_manager')
class MockPriceManager(azul.BasePriceManager):

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


class TestDownloadCommand(unittest.TestCase):

    def setUp(self):
        # Set start date a few days before today
        self.start_date_str = (datetime.datetime.now() - datetime.timedelta(days=4)).strftime('%Y-%m-%d')

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

        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir('test_data_dir')

            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'mock_price_manager',
                '--start', self.start_date_str,
                '--output-dir', 'test_data_dir'
            ])

            self.assertEqual(0, result.exit_code)
            expected = 'test_data_dir/minute'
            self.assertTrue(pathlib.Path(expected).exists())
            expected = 'test_data_dir/daily'
            self.assertTrue(pathlib.Path(expected).exists())


    def test_download_faang_iex(self):

        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir('test_data_dir')

            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'iex',
                '--start', self.start_date_str,
                '--output-dir', 'test_data_dir'
            ])

            self.assertEqual(0, result.exit_code)
            expected = 'test_data_dir/minute'
            self.assertTrue(pathlib.Path(expected).exists())
            expected = 'test_data_dir/daily'
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

