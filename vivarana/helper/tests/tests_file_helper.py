from django.test import SimpleTestCase
from django.core.files import File
import pandas as pd

import vivarana.helper.file_helper as file_helper
from vivarana.constants import TEST_DUMMY_FILE_PATH, TEST_CSV_FILE_PATH, TEST_LOG_FILE_PATH, TEMP_FILE_PATH


class TestFileUpload(SimpleTestCase):
    # def setUp(self):

    def test_handle_uploaded_dummy_file(self):
        """
        Tests uploaded dummy or unsupported files
        """
        f_dummy = open(TEST_DUMMY_FILE_PATH, 'rb')
        file_dummy_in = File(f_dummy)
        with open(TEMP_FILE_PATH, 'wb+') as destination:
            for chunk in file_dummy_in.chunks():
                destination.write(chunk)
        self.assertFalse(file_helper.handle_uploaded_file(file_dummy_in.name)['success'])
        self.assertEqual(file_helper.handle_uploaded_file(file_dummy_in.name)['error'],
                         'Sorry. File type xcel is not supported or parsing error occurred')

    def test_handle_uploaded_log_file(self):
        """
        Tests log file upload
        """
        f_log = open(TEST_LOG_FILE_PATH, 'rb')
        file_log_in = File(f_log)
        with open(TEMP_FILE_PATH, 'wb+') as destination:
            for chunk in file_log_in.chunks():
                destination.write(chunk)
        self.assertTrue(file_helper.handle_uploaded_file(file_log_in.name)['success'])
        self.assertIsInstance(file_helper.handle_uploaded_file(file_log_in.name)['dataframe'], pd.DataFrame)

    def test_handle_uploaded_csv_file(self):
        """
        Tests csv file upload
        """
        f_csv = open(TEST_CSV_FILE_PATH, 'rb')
        file_csv_in = File(f_csv)
        with open(TEMP_FILE_PATH, 'wb+') as destination:
            for chunk in file_csv_in.chunks():
                destination.write(chunk)
        self.assertTrue(file_helper.handle_uploaded_file(file_csv_in.name)['success'])
        self.assertIsInstance(file_helper.handle_uploaded_file(file_csv_in.name)['dataframe'], pd.DataFrame)


class TestDataFrameOperations(SimpleTestCase):
    def setUp(self):
        """
        opens a file and writes it to temp file in vivarana/media
        :return:self with a dataframe
        """
        f_log = open(TEST_LOG_FILE_PATH, 'rb')
        file_log_in = File(f_log)
        with open(TEMP_FILE_PATH, 'wb+') as destination:
            for chunk in file_log_in.chunks():
                destination.write(chunk)
        # get result from handle log file
        self.dataframe = file_helper.handle_uploaded_file(file_log_in.name)['dataframe']

    def test_get_data_summary(self):
        """
        tests data summary function
        """

        self.assertIsInstance(file_helper.get_data_summary(self.dataframe)['columns'], list)
        self.assertEqual(file_helper.get_data_summary(self.dataframe)['size'], 7)

    def test_remove_columns(self):
        """
        tests removal of unneeded columns
        """
        self.assertIsInstance(file_helper.remove_columns([1, 2], self.dataframe), pd.DataFrame)

    def test_get_compatible_column_names(self):
        """
        tests getting column types compatible with paracoords library function
        """
        self.assertIsInstance(file_helper.get_compatible_column_types(self.dataframe), dict)

    def test_get_html_friendly_names(self):
        """
        tests removal of illegal characters in the column names (HTML escaping) function
        """
        self.assertIsInstance(file_helper.get_html_friendly_names(self.dataframe.columns), list)


class TestColumnNameFormatting(SimpleTestCase):
    def test_remove_illegal_characters(self):
        """
        tests function to remove illegal characters
        """
        self.assertEqual(file_helper.remove_illegal_characters("str^5"), 'str5')


if __name__ == '__main__':
    # suite1 = SimpleTestCase.TestLoader().loadTestsFromTestCase(TestFileUpload)
    # suite2 = SimpleTestCase.TestLoader().loadTestsFromTestCase(TestDataFrameOperations)
    # suite3 = SimpleTestCase.TestLoader().loadTestsFromTestCase(TestColumnNameFormatting)
    # alltests = SimpleTestCase.TestSuite([suite1, suite2,suite3])
    # SimpleTestCase.TextTestRunner(verbosity=2).run(alltests)
    SimpleTestCase.main()

