import unittest
import tempfile
import azul
import pathlib
import shutil

FAANG_FETCHER = 'faang'


class TestWriteSymbols(unittest.TestCase):

    def delete_test_symbols(self):
        # The tests create some test files which should be removed before and after the tests run.
        try:
            pathlib.Path.unlink(self.test_symbols_file_path)
        except FileNotFoundError as e:
            pass
        self.assertFalse(pathlib.Path(self.test_symbols_file_path).exists())

    def setUp(self):
        self.test_symbols_file_path = pathlib.Path.home() / ('.azul/symbols/' + FAANG_FETCHER + '.txt')
        self.delete_test_symbols()
        self.source = FAANG_FETCHER

    def tearDown(self):
        self.delete_test_symbols()

    def test_writes_symbols_to_home_directory_when_nothing_is_specified(self):
        #  Scenario 1: Nothing was specified:
        #  Create a default symbols file in default symbols path.

        # Given there is no test.txt file in the home directory
        self.delete_test_symbols()

        # When write_symbols is called with no output_location specified
        azul.write_symbols(source=FAANG_FETCHER, output_path=None)

        # Then there will be a test.txt file written to the home directory
        self.assertTrue(pathlib.Path(self.test_symbols_file_path).exists())

    def test_overwrites_symbols_file_when_one_exists(self):
        # Scenario 2: The file exists:
        # Overwrite it.

        # Given an existing symbols file
        f = tempfile.NamedTemporaryFile()

        # When write_symbols is asked to overwrite it
        azul.write_symbols(source=FAANG_FETCHER, output_path=f.name)

        # Then it does.
        actual = pathlib.Path(f.name).read_text()
        expected = 'GOOG\n'
        self.assertEqual(actual, expected)
        f.close()

    def test_writes_symbols_to_a_default_file_when_existing_directory_specified(self):
        # Scenario 3: The directory exists but no file specified:
        # Create a default symbols file in the existing directory.

        # Given an existing directory
        dir_path = tempfile.mkdtemp()

        # When write_symbols is called with an existing directory but no filename
        azul.write_symbols(source=FAANG_FETCHER, output_path=dir_path)

        # Then it creates a default file in the existing directory.
        expected_path = pathlib.Path(dir_path) / (FAANG_FETCHER + '.txt')
        self.assertTrue(pathlib.Path(expected_path).exists())

        # cleanup
        shutil.rmtree(dir_path)

    def test_writes_symbols_to_a_default_file_when_non_existent_directory_specified(self):
        # Scenario 4: The file wasn't specified and the parent directory doesn't exist.
        # Create the directory with a default file.

        # Given a non-existent directory
        non_existent_specified_directory = tempfile.gettempdir() + '/azul_tests/'
        # First, make sure it doesn't exist
        try:
            pathlib.Path.unlink(pathlib.Path(non_existent_specified_directory))
        except FileNotFoundError:
            pass
        self.assertFalse(pathlib.Path(non_existent_specified_directory).exists())

        # When write_symbols is called with a non existent directory and unspecified file
        azul.write_symbols(source=FAANG_FETCHER, output_path=non_existent_specified_directory)

        # Then it creates a default file in the new directory
        expected_path = pathlib.Path(non_existent_specified_directory + FAANG_FETCHER + '.txt')
        self.assertTrue(pathlib.Path(expected_path).exists())

        # cleanup
        shutil.rmtree(non_existent_specified_directory)

    def test_writes_symbols_to_a_specified_file_when_directory_exists_but_not_file(self):
        # Scenario 5a: The directory and file were specified and the directory exists but the file doesn't
        # Create the specified file in the existing directory.

        # Given an existing directory
        dir_path = tempfile.mkdtemp()
        # And a file that doesn't exist
        specified_file_path = dir_path + '/my_test.txt'
        # First, make sure it doesn't exist
        try:
            pathlib.Path.unlink(pathlib.Path(specified_file_path))
        except FileNotFoundError:
            pass

        # When write_symbols is asked to put symbols in it
        azul.write_symbols(source=FAANG_FETCHER, output_path=specified_file_path)

        # Then it creates a default file in in.
        expected_path = pathlib.Path(specified_file_path)
        self.assertTrue(pathlib.Path(expected_path).exists())

        # cleanup
        shutil.rmtree(dir_path)

    def test_creates_the_directory_and_file_when_both_are_specified_and_non_existent(self):
        # Scenario 5b: The directory and file were specified and both directory and file don't exist
        # Create the specified file and any parent directories.

        # Given a non-existent directory and non-existent file
        non_existent_specified_directory = tempfile.gettempdir() + '/azul_tests'
        non_existent_specified_file_path = non_existent_specified_directory + '/mytest.txt'
        # First, make sure it doesn't exist
        try:
            pathlib.Path.unlink(pathlib.Path(non_existent_specified_directory))
        except FileNotFoundError:
            pass

        # When write_symbols is asked to put symbols in it
        azul.write_symbols(source=FAANG_FETCHER, output_path=non_existent_specified_file_path)

        # Then it creates the specified file in the new directory
        expected_path = pathlib.Path(non_existent_specified_file_path)
        self.assertTrue(pathlib.Path(expected_path).exists())

        # cleanup
        shutil.rmtree(non_existent_specified_directory)

