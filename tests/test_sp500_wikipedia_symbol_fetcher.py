import unittest
from azul import symbol_fetcher_registry


class TestSP500WikiSymbolFetcher(unittest.TestCase):

    def test_returns_the_right_symbols(self):
        sym_fetcher = symbol_fetcher_registry.get('sp500_wikipedia')
        actual = sym_fetcher.symbols()
        self.assertEqual(505, len(actual))
        expected = ['BK', 'CI', 'JPM', 'DD-B', 'CL', 'HIG']
        self.assertFalse(set(expected).isdisjoint(actual))
