import unittest
import click
from click.testing import CliRunner
import azul


class TestWriteSymbols(unittest.TestCase):

    def test_download_sp500(self):

        runner = CliRunner()
        result = runner.invoke(azul.azul_cli, ['download'])
        self.assertEqual(0, result.exit_code)
        print(result.output)