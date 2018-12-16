import unittest
import tempfile
import azul
import pathlib
import shutil


class TestWriteSymbols(unittest.TestCase):

    def delete_test_symbols(self):
        # The tests create some test files which should be removed before and after the tests run.
        try:
            pathlib.Path.unlink(self.test_symbols_file_path)
        except FileNotFoundError as e:
            pass

    def setUp(self):
        self.test_symbols_file_name = '.azul/symbols/test.txt'
        self.test_symbols_file_path = pathlib.Path.home() / self.test_symbols_file_name
        self.delete_test_symbols()

    def tearDown(self):
        self.delete_test_symbols()

    def test_writes_symbols_to_home_directory_when_nothing_is_specified(self):

        # Given there is no test_symbols.txt file in the home directory
        self.assertFalse(pathlib.Path(self.test_symbols_file_path).exists())

        # WHEN a call to write_symbols is made and no output_location is specified
        azul.write_symbols(source='test', output_location=None)

        # Then there will be a test_symbols.txt file written to the home directory
        self.assertTrue(pathlib.Path(self.test_symbols_file_path).exists())

    def test_overwrites_symbols_file_when_one_exists(self):

        # Given an existing symbols file
        f = tempfile.NamedTemporaryFile()

        # When write_symbols is asked to overwrite it
        azul.write_symbols(source='test', output_location=f.name)

        # Then it does.
        actual = pathlib.Path(f.name).read_text()
        expected = 'test_symbol'
        self.assertEqual(actual, expected)
        f.close()

    def test_writes_symbols_to_a_default_file_when_existing_directory_specified(self):

        # Given an existing directory
        dir_path = tempfile.mkdtemp()

        # When write_symbols is asked to put symbols in it
        azul.write_symbols(source='test', output_location=dir_path)

        # Then it creates a default file in in.
        expected_path = pathlib.Path(dir_path) / 'test.txt'
        self.assertTrue(pathlib.Path(expected_path).exists())

        # cleanup
        shutil.rmtree(dir_path)

    def test_writes_symbols_to_a_specified_file_when_directory_exists_but_not_file(self):

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
        azul.write_symbols(source='test', output_location=specified_file_path)

        # Then it creates a default file in in.
        expected_path = pathlib.Path(specified_file_path)
        self.assertTrue(pathlib.Path(expected_path).exists())

        # cleanup
        shutil.rmtree(dir_path)

    def test_creates_the_directory_and_file_when_both_are_specified_and_non_existent(self):

        # Given a non-existent directory and non-existent file
        non_existent_specified_directory = tempfile.gettempdir() + '/azul_tests'
        non_existent_specified_file_path = non_existent_specified_directory + '/mytest.txt'
        # First, make sure it doesn't exist
        try:
            pathlib.Path.unlink(pathlib.Path(non_existent_specified_directory))
        except FileNotFoundError:
            pass

        # When write_symbols is asked to put symbols in it
        azul.write_symbols(source='test', output_location=non_existent_specified_file_path)

        # Then it creates the specified file in the new directory
        expected_path = pathlib.Path(non_existent_specified_file_path)
        self.assertTrue(pathlib.Path(expected_path).exists())

        # cleanup
        shutil.rmtree(non_existent_specified_directory)

    def test_writes_symbols_to_a_default_file_when_non_existent_directory_specified(self):

        # Given a non-existent directory
        non_existent_specified_directory = tempfile.gettempdir() + '/azul_tests/'
        # First, make sure it doesn't exist
        try:
            pathlib.Path.unlink(pathlib.Path(non_existent_specified_directory))
        except FileNotFoundError:
            pass

        # When write_symbols is asked to put symbols in it
        azul.write_symbols(source='test', output_location=non_existent_specified_directory)

        # Then it creates a default file in the new directory
        expected_path = pathlib.Path(non_existent_specified_directory + '/test.txt')
        print(expected_path)
        self.assertTrue(pathlib.Path(expected_path).exists())

        # cleanup
        shutil.rmtree(non_existent_specified_directory)
