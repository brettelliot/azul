import logbook
from class_registry import ClassRegistry
from class_registry import RegistryKeyError
from .symbol_fetcher import SymbolFetcher
from .scripts.azul import azul_cli

__all__ = [
    'write_symbols',
    'SymbolFetcher',
    'azul_cli'
]

symbol_fetcher_registry = ClassRegistry()
from .faang_symbol_fetcher import FaangSymbolFetcher


def write_symbols(source, output_path):
    """
    Get a list of symbols from source and write them to outfile.

    Args:
        source (str):
            The source of the symbol list.
            ``sp500`` will provide the list of symbols in the S&P 500 index.
            ``polygon_cs`` will provide the list of common stocks available on Polygon.io
            ``iex`` will provide the list of symbols available on IEX.
            ``faang`` will provide a small list of symbols (FAANG) for testing.
        output_path (str):
            The output filename or directory where the symbol list will be written. If a directory is specified, a
            default filename will be used. If nothing is specified the symbol list will be created in: ~/.azul/symbols

    Returns:
        None
    """
    # Set the logger
    log = logbook.Logger('WriteSymbols')

    try:
        sym_fetcher = symbol_fetcher_registry.get(source, output_path)
    except RegistryKeyError:
        log.error('No symbol fetcher registered with key: %s', source)
        raise

    # Get the real output path for storing the symbols
    default_filename = source + '.txt'
    output_path = sym_fetcher.get_symbols_file_path(output_path, default_filename)
    #output_path.write_text('test_symbol')

    # Get the symbols
    symbols = sym_fetcher.symbols()

    # Write the symbols out
    sym_fetcher.write_symbols_to_file(symbols, output_path)


def download_symbols(symbol_source, data_source, output_dir, start):
    print(symbol_source, data_source, output_dir, start)
    pass

