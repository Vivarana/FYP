from django.test import SimpleTestCase
from django.core.files import File
import pandas as pd

import vivarana.helper.file_helper as file_helper
from vivarana.constants import TEST_DUMMY_FILE_PATH, TEST_CSV_FILE_PATH, TEST_LOG_FILE_PATH


class FileUploadTestCase(SimpleTestCase):
    # def setUp(self):
    #setup test

    def test_handle_uploaded_dummy_file(self):
        """
        Tests uploaded dummy or unsupported files
        """
        f_dummy = open(TEST_DUMMY_FILE_PATH, 'rb')
        file_dummy_in = File(f_dummy)
        self.assertFalse(file_helper.handle_uploaded_file(file_dummy_in)['success'])
        self.assertEqual(file_helper.handle_uploaded_file(file_dummy_in)['error'],
                         'Sorry. File type xcel is not supported or parsing error occurred')

    def test_handle_uploaded_log_file(self):
        """
        Tests log file upload
        """
        f_log = open(TEST_LOG_FILE_PATH, 'rb')
        file_log_in = File(f_log)
        self.assertTrue(file_helper.handle_uploaded_file(file_log_in)['success'])
        self.assertIsInstance(file_helper.handle_uploaded_file(file_log_in)['dataframe'], pd.DataFrame)

    def test_handle_uploaded_csv_file(self):
        """
        Tests csv file upload
        """
        f_csv = open(TEST_CSV_FILE_PATH, 'rb')
        file_csv_in = File(f_csv)
        self.assertTrue(file_helper.handle_uploaded_file(file_csv_in)['success'])
        self.assertIsInstance(file_helper.handle_uploaded_file(file_csv_in)['dataframe'], pd.DataFrame)


if __name__ == '__main__':
    SimpleTestCase.main()