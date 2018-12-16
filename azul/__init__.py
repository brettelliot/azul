import pathlib
import os
import logbook


__all__ = [
    'write_symbols',

]


def write_symbols(source, output_location):
    """
    Get a list of symbols from source and write them to outfile.

    Args:
        source (str):
            The source of the symbol list.
            ``sp500`` will provide the list of symbols in the S&P 500 index.
            ``polygon_cs`` will provide the list of common stocks available on Polygon.io
            ``iex`` will provide the list of symbols available on IEX.
            ``test`` will provide a small list of symbols for testing.
        output_location (str):
            The output filename or directory where the symbol list will be written. If a directory is specified, a
            default filename will be used. If nothing is specified the symbol list will be created in: ~/.azul/symbols

    Returns:
        None
    """
    # Set the logger
    log = logbook.Logger('WriteSymbols')

    valid_sources = ['sp500', 'iex', 'polygon_cs', 'test']
    if source not in valid_sources:
        raise ValueError('This is not a valid source:', source)

    """
    Scenarios:
        Nothing was specified: Create a default symbols file in the ~/.azul/symbols
        The file exists: Overwrite it.
        The directory exists but no file specified: Create a default symbols file in the existing directory.
        The directory exists but not the specified file: Create the specified file in the existing directory.
        Neither the specified directory nor the specified file exist: Create the directory with the file.
        The directory does not exist but no file was specified: Create a default symbol file in a new directory.
    """

    default_filename = source + '.txt'
    if output_location is None:
        log.debug('Nothing was specified.')
        # Nothing was specified.
        # Create the directory ~/.azul/symbols if it doesn't exist
        default_symbols_path = pathlib.Path.home() / '.azul/symbols'
        pathlib.Path(default_symbols_path).mkdir(parents=True, exist_ok=True)
        # Create a default symbols file in there.
        output_path = pathlib.Path(default_symbols_path) / default_filename
        output_path.touch()
    else:
        # Some output location was specified
        output_path = pathlib.Path(output_location)
        if output_path.is_file():
            log.debug('The file exists.')
        elif output_path.is_dir():
            log.debug('The directory exists but no file specified.')
            # Create a default symbols file in there.
            output_path = pathlib.Path(output_location) / default_filename
            output_path.touch()
        else:
            # Whatever it is, it doesn't exist yet. Let's see if they wanted a file or a directory:
            base = os.path.basename(output_location)
            if base == '':
                log.debug('Its a non-existent directory')
                # Create the directory.
                pathlib.Path(output_location).mkdir(parents=True, exist_ok=True)
                # Create a default symbols file in there.
                output_path = pathlib.Path(output_location) / default_filename
                output_path.touch()
            else:
                log.debug('Its a non-existent file in a possibly non-existent directory:')
                parent_location = os.path.dirname(output_location)
                # Create the parent directory.
                pathlib.Path(parent_location).mkdir(parents=True, exist_ok=True)
                output_path = pathlib.Path(parent_location) / base
                output_path.touch()

    output_path.write_text('test_symbol')


