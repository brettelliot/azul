import azul


@azul.symbol_fetcher_registry.register('faang')
class FaangSymbolFetcher(azul.SymbolFetcher):

    def __init__(self, symbols_path=None):
        super().__init__(symbols_path)
        pass

    def symbols(self):
        return ['FB', 'AMZN', 'AAPL', 'NFLX', 'GOOG']

