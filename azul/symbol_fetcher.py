import pathlib
import logbook

log = logbook.Logger('SymbolFetcher')


class SymbolFetcher(object):

    def __init__(self, symbols_path=None):
        if symbols_path is None:
            # Create a default directory for storing symbols
            symbols_path = pathlib.Path.home() / '.azul/symbols'
            # Create the directory if it doesn't exist
            pathlib.Path(symbols_path).mkdir(parents=True, exist_ok=True)
        # Set the path for any default symbols files
        self.symbols_path = symbols_path

        # Define valid sources
        self.valid_sources = ['sp500', 'iex', 'polygon_cs', 'test']

    def is_valid_source(self, source):
        if source in self.valid_sources:
            return True
        else:
            return False

    def get_symbols_file_path(self, output_path=None, default_filename='symbols.txt'):
        """
        Takes an output location (possibly specified on the command line) and turns it into a file path to a real file.

        Args:
            output_path (str):
                Either a file or a directory, (both of which may or may not exist) or None. If file and/ or parent
                directories in the output location don't exist they will be created. If None is specified then a default
                filename is used and written to the self.symbols_path.
            default_filename (str):
                If no filename is passed in we will create symbols file using this filename.

        Returns:
            None

        Scenarios:
            Scenario 1: Nothing was specified:
                Create a default symbols file in default symbols path.
            Scenario 2: The file exists:
                Overwrite it.
            Scenario 3: The directory exists but no file specified:
                Create a default symbols file in the existing directory.
            Scenario 4: The file wasn't specified and the parent directory doesn't exist.
                Create the directory with a default file.
            Scenario 5: The directory and file were specified but either or both do not exist.
                Create the specified file and any parent directories.
        """
        if output_path is None:
            # Scenario 1: Nothing was specified
            # Create a default symbols file in default symbols path.
            log.debug('Nothing was specified.')
            ret_path = pathlib.Path(self.symbols_path) / default_filename
        else:
            # Some output location was specified
            output_path = pathlib.Path(output_path)
            if output_path.is_file():
                # Scenario 2: The file exists: Overwrite it.
                log.debug('The file exists.')
                ret_path = output_path
            elif output_path.is_dir():
                # Scenario 3: The directory exists but no file specified.
                # Create a default symbols file in the existing directory.
                log.debug('The directory exists but no file specified.')
                ret_path = pathlib.Path(output_path) / default_filename
            else:
                # Whatever it is, it doesn't exist yet. Let's see if they wanted a file or a directory:
                suffix = output_path.suffix
                if suffix == '':
                    # Scenario 4: The file wasn't specified and the parent directory doesn't exist.
                    # Create the directory with a default file.
                    log.debug('Its a non-existent directory')
                    # Create the directory.
                    pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
                    # Create a default symbols file in there.
                    ret_path = pathlib.Path(output_path) / default_filename
                else:
                    # Scenario 5: The directory and file were specified but either one the other do not exist.
                    # Create the specified file and any parent directories (if needed).
                    log.debug('Its a non-existent file in a possibly non-existent directory:')
                    parent_location = output_path.parent
                    # Create the parent directory.
                    pathlib.Path(parent_location).mkdir(parents=True, exist_ok=True)
                    ret_path = pathlib.Path(parent_location) / output_path.name

        ret_path.touch()
        return ret_path
