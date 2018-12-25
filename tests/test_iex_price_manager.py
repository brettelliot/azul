import unittest
from click.testing import CliRunner
import azul
import os
import pathlib
import pandas as pd
import shutil
import datetime



class TestIEPriceManager(unittest.TestCase):

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

    def test_download_faang_iex(self):

        output_dir_str = 'test__iex_data_dir'

        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir(output_dir_str)

            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'iex',
                '--start', self.start_date_str,
                '--output-dir', output_dir_str
            ])

            self.assertEqual(0, result.exit_code)
            expected = output_dir_str + '/minute'
            self.assertTrue(pathlib.Path(expected).exists())
            expected = output_dir_str + '/daily'
            self.assertTrue(pathlib.Path(expected).exists())
