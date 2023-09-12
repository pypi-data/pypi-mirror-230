import pathlib
import unittest

import pivtestdata as ptd

__this_dir__ = pathlib.Path(__file__).parent


class TestPIVTec(unittest.TestCase):

    def test_version(self):
        self.assertEqual(ptd.__version__, '0.2.0')

    def test_filesizes(self):
        self.assertEqual(ptd.pivtec.vortex_pair.file_size, 11646143)

    def test_delete_all(self):
        ptd.delete_all_downloaded_files()
        self.assertFalse(ptd.user_dir.exists())
