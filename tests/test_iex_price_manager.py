import unittest
from click.testing import CliRunner
import azul
import os
import pathlib
import pandas as pd
import shutil
from datetime import datetime, timedelta


class TestIEPriceManager(unittest.TestCase):

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

    #@unittest.skip
    def test_download_faang_iex(self):

        # Given a place to store the data
        output_dir_str = 'test_iex_data_dir'

        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir(output_dir_str)

            # When azul is asked to download FAANG data from IEX
            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'iex',
                '--start', self.start_date_str,
                '--output-dir', output_dir_str
            ])

            # Then it gets 30 days of minute and daily data.
            self.assertEqual(0, result.exit_code)
            expected = output_dir_str + '/minute'
            self.assertTrue(pathlib.Path(expected).exists())
            expected = output_dir_str + '/daily'
            self.assertTrue(pathlib.Path(expected).exists())

    #@unittest.skip
    def test_download_iex_handles_unavailable_dates_gracefully(self):

        # Given a place to store the data
        output_dir_str = 'test_iex_data_dir'

        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir(output_dir_str)

            # When azul is asked to download more than 30 days of data from IEX
            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'iex',
                '--start', '2017-01-01',
                '--output-dir', output_dir_str
            ])

            # Then it gets the last 30 days of minute and daily data.
            self.assertEqual(0, result.exit_code)
            expected = output_dir_str + '/minute'
            self.assertTrue(pathlib.Path(expected).exists())
            expected = output_dir_str + '/daily'
            self.assertTrue(pathlib.Path(expected).exists())

    def test_validated_dates_handles_unavailable_dates_gracefully(self):

        # Given a start date of over 30 days ago
        start_date = datetime(2011,12,25)
        today = datetime.today()
        thirty_days_ago = today - timedelta(days=30)
        end_date = today

        # When IEX price manager validates that start date
        pm = azul.price_manager_registry.get('iex')
        actual_start_date, actual_end_date = pm._validated_start_and_end_dates(start_date, end_date)

        # Then the start date is actually 30 days ago
        self.assertEqual(thirty_days_ago.date(), actual_start_date.date())
        self.assertEqual(today.date(), actual_end_date.date())
