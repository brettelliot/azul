from azul import symbol_fetcher_registry, BaseSymbolFetcher
import pandas as pd
from typing import List

@symbol_fetcher_registry.register('sp500_wikipedia')
class SP500WikipediaSymbolFetcher(BaseSymbolFetcher):

    def __init__(self):
        super().__init__()

    def symbols(self) -> List[str]:
        """

        Returns:
            symbols (List[str]): A list containing all the ticker symbols of the S&P500 stocks

        """
        data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        table = data[0]
        sliced_table = table[1:]
        header = table.iloc[0]
        df = sliced_table.rename(columns=header)
        symbols = df['Symbol'].tolist()
        return symbols

