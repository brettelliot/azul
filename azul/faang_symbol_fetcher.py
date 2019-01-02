from azul import symbol_fetcher_registry, BaseSymbolFetcher


@symbol_fetcher_registry.register('faang')
class FaangSymbolFetcher(BaseSymbolFetcher):

    def __init__(self):
        super().__init__()

    def symbols(self):
        return ['FB', 'AMZN', 'AAPL', 'NFLX', 'GOOG']

