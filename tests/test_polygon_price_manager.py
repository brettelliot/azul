import unittest
from azul import price_manager_registry
from datetime import datetime, timedelta
from click.testing import CliRunner
import tempfile
import pathlib
import azul


class TestPolygonPriceManager(unittest.TestCase):

    def setUp(self):
        # Set start date a few days before today
        self.start_date_str = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')

    # This test will only pass when the AZUL_POLYGON_API_KEY is not set.
    @unittest.skip
    def test_raise_value_error_if_no_env_var_set(self):
        with self.assertRaises(ValueError):
            pm = price_manager_registry.get('polygon')

    def test_env_var_set(self):
        pm = price_manager_registry.get('polygon')

    def test_download_faang_polygon(self):

        # Given a directory for the data to be downloaded.
        with tempfile.TemporaryDirectory() as output_dir_name:
            output_dir_path = pathlib.Path(output_dir_name)

            # When azul is asked to download FAANG data from IEX
            runner = CliRunner()
            result = runner.invoke(azul.cli, [
                'download',
                '--symbol-source', 'faang',
                '--data-source', 'polygon',
                '--start', self.start_date_str,
                '--output-dir', output_dir_name
            ])

            self.assertEqual(0, result.exit_code)
            expected = pathlib.Path(output_dir_path, 'minute')
            self.assertTrue(pathlib.Path(expected).exists())
            expected = pathlib.Path(output_dir_path, 'daily')
            self.assertTrue(pathlib.Path(expected).exists())

    @unittest.skip
    def test_polygon_throttling(self):
        # Run this in the debugger and see what's going on. It gets a year of minute data from polygon.

        # Given an existing data dir
        with tempfile.TemporaryDirectory() as output_dir_name:
            output_dir_path = pathlib.Path(output_dir_name)

            # With data up to a week ago
            symbol_source = 'sp500_wikipedia'
            data_source = 'polygon'
            start_date = datetime.strptime('2018-01-01', azul.FORMAT_YMD)
            end_date = datetime.strptime('2019-01-01', azul.FORMAT_YMD)
            azul.get_price_data(symbol_source, data_source, output_dir_path, start_date, end_date)
