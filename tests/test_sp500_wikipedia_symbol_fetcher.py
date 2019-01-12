import unittest
from azul import symbol_fetcher_registry


class TestSP500WikiSymbolFetcher(unittest.TestCase):

    def test_can_fetch_sp500_symbols_from_wikipedia(self):
        """
        Tests that the SP500WikipediaSymbolFetcher can:
            * fetch the SP500 symbols from wikipedia
        """

        # Given the SP500WikipediaSymbolFetcher
        sym_fetcher = symbol_fetcher_registry.get('sp500_wikipedia')

        # When asked to fetch symbols
        actual = sym_fetcher.symbols()

        # Then make sure we got all of them
        self.assertEqual(505, len(actual))

        # And make sure a sampling of know stocks are in the list
        expected = ['BK', 'CI', 'JPM', 'DD-B', 'CL', 'HIG']
        self.assertFalse(set(expected).isdisjoint(actual))
