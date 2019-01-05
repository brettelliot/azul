import unittest
from azul import symbol_fetcher_registry


class TestFaangSymbolFetcher(unittest.TestCase):

    def test_returns_the_right_symbols(self):
        sym_fetcher = symbol_fetcher_registry.get('faang')
        actual = sym_fetcher.symbols()
        expected = ['FB', 'AMZN', 'AAPL', 'NFLX', 'GOOG']
        self.assertFalse(set(expected).isdisjoint(actual))
