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
