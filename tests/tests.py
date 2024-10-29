import unittest
from unittest import mock

from main import (
    get_time_limit
)

class TestDeletionMethods(unittest.TestCase):

    def test_get_time_limit(self):
        limit = get_time_limit()
        assert type(limit) is int()



if __name__=='__main__':
    unittest.main()