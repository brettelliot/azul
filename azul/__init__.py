import logbook
from .symbol_fetcher import SymbolFetcher


__all__ = [
    'write_symbols',
    'SymbolFetcher'
]


def write_symbols(source, output_path):
    """
    Get a list of symbols from source and write them to outfile.

    Args:
        source (str):
            The source of the symbol list.
            ``sp500`` will provide the list of symbols in the S&P 500 index.
            ``polygon_cs`` will provide the list of common stocks available on Polygon.io
            ``iex`` will provide the list of symbols available on IEX.
            ``test`` will provide a small list of symbols for testing.
        output_path (str):
            The output filename or directory where the symbol list will be written. If a directory is specified, a
            default filename will be used. If nothing is specified the symbol list will be created in: ~/.azul/symbols

    Returns:
        None
    """
    # Set the logger
    log = logbook.Logger('WriteSymbols')

    sym_fetcher = SymbolFetcher()

    if not sym_fetcher.is_valid_source(source):
        raise ValueError('This is not a valid source:', source)

    # Get the real output path for storing the symbols
    default_filename = source + '.txt'
    output_path = sym_fetcher.get_symbols_file_path(output_path, default_filename)
    output_path.write_text('test_symbol')

