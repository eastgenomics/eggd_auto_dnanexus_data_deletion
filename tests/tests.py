import unittest
from unittest import mock
from unittest.mock import patch
import time

from main import (
    get_time_limit,
    find_files,
    tar_details
)

class TestDeletionMethods(unittest.TestCase):

    def test_get_time_limit(self):
        limit = get_time_limit()
        assert type(limit) is int()

    # test limit is in milliseconds?

    #test find files
    ## mock/patch dx.api.system_find_data_objects

    @patch('main.dx.api.system_find_data_objects')
    def test_find_files(self, mock_find):

        now = round(time.time()) * 1000
        
        #reduced version of the dx api output
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
                    "createdBy": {
                    "user": "user-jsims"
                    },
                    "media": "application/gzip",
                    "archivalState": "live",
                }
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
                    "createdBy": {
                    "user": "user-jsims"
                    },
                    "media": "application/gzip",
                    "archivalState": "live",
                    }
                }
            ],
            "next": {
                "project": "project-XXXXXXXXX",
                "id": "file-CCCCCCCCCCCC"
            }
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
                    "createdBy": {
                    "user": "user-jsims"
                    },
                    "media": "application/gzip",
                    "archivalState": "live",
                }
                }
            ]

        files = find_files('fake-project', 86400 * 1000 )
        self.assertEqual([files[0]], expectd_results)

    # test tar details
    ##test project
    ##test csv format
    ## independent test of object/tar file age?

    def test_tar_details(self):

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
                    "createdBy": {
                    "user": "user-jsims"
                    },
                    "media": "application/gzip",
                    "archivalState": "live",
                }
                }
            ]

        expected_details = ['run.A_RUN_NAME.lane.all_004.tar.gz,file-AAAAAAAAAAA,project-XXXXXXXXX']

        self.assertEqual(tar_details(found_tars), expected_details)

    #test output of tar details
    ## test lines = n of tar files
    ## test csv format



if __name__=='__main__':
    unittest.main()