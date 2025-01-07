import dxpy as dx
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest import mock, skip
from unittest.mock import patch

import time

from main import get_time_limit, find_files, tar_details


class Test_DNAnexus_login_authenitication:
    def test_time_is_int(self):
        limit = get_time_limit()
        assert isinstance(limit, int)


class Test_file_retrival(unittest.TestCase):
    # @skip("don't think this can be tested as it's just a wrapper for dx api")
    @patch("main.dx.find_data_objects")
    def test_found_files_are_older_than_age_limit(self, mock_find):

        now = round(time.time()) * 1000

        # reduced version of the dx api output
        mock_find.return_value = {
            "results": [
                {
                    "project": "project-XXXXXXXXX",
                    "id": "file-AAAAAAAAAAA",
                    "describe": {
                        "id": "file-AAAAAAAAAAA",
                        "project": "project-XXXXXXXXX",
                        "class": "file",
                        "name": "run.A_RUN_NAME.lane.all_004.tar.gz",
                        "folder": "/fake_runfolder_01/runs",
                        "created": 1728913404000,
                        "modified": 1728913406925,
                        "createdBy": {"user": "user-jsims"},
                        "media": "application/gzip",
                        "archivalState": "live",
                    },
                },
                {
                    "project": "project-XXXXXXXXX",
                    "id": "file-BBBBBBBBBBB",
                    "describe": {
                        "id": "file-BBBBBBBBBBB",
                        "project": "project-XXXXXXXXX",
                        "class": "file",
                        "name": "run.A_RUN_NAME.lane.all_001.tar.gz",
                        "folder": "/fake_runfolder_01/runs",
                        f"created": {now},
                        f"modified": {now},
                        "createdBy": {"user": "user-jsims"},
                        "media": "application/gzip",
                        "archivalState": "live",
                    },
                },
            ],
            "next": {"project": "project-XXXXXXXXX", "id": "file-CCCCCCCCCCCC"},
        }

        expectd_results = [
            {
                "project": "project-XXXXXXXXX",
                "id": "file-AAAAAAAAAAA",
                "describe": {
                    "id": "file-AAAAAAAAAAA",
                    "project": "project-XXXXXXXXX",
                    "class": "file",
                    "name": "run.A_RUN_NAME.lane.all_004.tar.gz",
                    "folder": "/fake_runfolder_01/runs",
                    "created": 1728913404000,
                    "modified": 1728913406925,
                    "createdBy": {"user": "user-jsims"},
                    "media": "application/gzip",
                    "archivalState": "live",
                },
            }
        ]

        files = find_files("fake-project", 1728913404001)
        results = files["results"]
        print(expectd_results)
        self.assertEqual(results, expectd_results)


class Test_file_data_extraction(unittest.TestCase):
    def test_csv_details_extraction(self):

        found_tars = [
            {
                "project": "project-XXXXXXXXX",
                "id": "file-AAAAAAAAAAA",
                "describe": {
                    "id": "file-AAAAAAAAAAA",
                    "project": "project-XXXXXXXXX",
                    "class": "file",
                    "name": "run.A_RUN_NAME.lane.all_004.tar.gz",
                    "folder": "/fake_runfolder_01/runs",
                    "created": 1728913404000,
                    "modified": 1728913406925,
                    "createdBy": {"user": "user-jsims"},
                    "media": "application/gzip",
                    "archivalState": "live",
                    "size": 900,
                },
            }
        ]

        expected_details = pd.DataFrame(
            {
                "name": ["run.A_RUN_NAME.lane.all_004.tar.gz"],
                "file": ["file-AAAAAAAAAAA"],
                "project": ["project-XXXXXXXXX"],
                "size": [900],
            }
        )
        print(tar_details(found_tars))
        assert_frame_equal(tar_details(found_tars), expected_details)


class Test_write_file_details:
    pass
