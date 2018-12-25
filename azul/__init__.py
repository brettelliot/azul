import logbook
from class_registry import ClassRegistry
from class_registry import RegistryKeyError
from .symbol_fetcher import SymbolFetcher
from .scripts.azul import cli
from .base_price_manager import BasePriceManager
import pathlib
from datetime import datetime

__all__ = [
    'write_symbols',
    'get_price_data',
    'SymbolFetcher',
    'cli',
    'BasePriceManager',
    'FORMAT_YMD'
]

symbol_fetcher_registry = ClassRegistry()
from .faang_symbol_fetcher import FaangSymbolFetcher

price_manager_registry = ClassRegistry()
from .polygon_price_manager import PolygonPriceManager
from .iex_price_manager import IEXPriceManager


FORMAT_YMD = "%Y-%m-%d"

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


def get_price_data(symbol_source: str, data_source: str, output_dir: str, start: datetime, end: datetime) -> None:
    """
    Gets symbols, downloads minute data, generates daily data, and stores it in output_dir.

    Args:
        symbol_source (str):
            The source of the symbols.
            ``sp500`` will provide the list of symbols in the S&P 500 index.
            ``polygon_cs`` will provide the list of common stocks available on Polygon.io
            ``iex`` will provide the list of symbols available on IEX.
            ``faang`` will provide a small list of symbols (FAANG) for testing.
        data_source (str):
            The source of the price data.
            ``polygon`` will get price data from polygon.io
            ``iex`` will get price data from IEX.
        output_dir (str):
            The directory to store the data in.
        start (datetime):
            The date to start getting data from.
        end (datetime):
            The date to end getting data from.

    Returns:
        None

    """
    # Set the logger
    log = logbook.Logger('get_price_data')

    try:
        sym_fetcher = symbol_fetcher_registry.get(symbol_source, output_dir)
    except RegistryKeyError:
        log.error('No symbol fetcher registered with key: %s', symbol_source)
        raise

    # Get the symbols
    symbols = sym_fetcher.symbols()

    # Get the price manager
    try:
        price_manager = price_manager_registry.get(data_source)
    except RegistryKeyError:
        log.error('No price manager registered with key: %s', data_source)
        raise

    if output_dir is None:
        # Create a default directory for storing data
        default_output_dir_name = '.azul/' + data_source
        default_output_dir_path = pathlib.Path.home() / default_output_dir_name
        # Create the directory if it doesn't exist
        pathlib.Path(default_output_dir_path).mkdir(parents=True, exist_ok=True)
        output_dir = str(default_output_dir_path)

    price_manager.get_price_data(symbols, output_dir, start, end)



