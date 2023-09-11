"""
    lakeFS API

    lakeFS HTTP API  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Contact: services@treeverse.io
    Generated by: https://openapi-generator.tech
"""


import unittest

import lakefs_client
from lakefs_client.api.retention_api import RetentionApi  # noqa: E501


class TestRetentionApi(unittest.TestCase):
    """RetentionApi unit test stubs"""

    def setUp(self):
        self.api = RetentionApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_delete_garbage_collection_rules(self):
        """Test case for delete_garbage_collection_rules

        """
        pass

    def test_get_garbage_collection_rules(self):
        """Test case for get_garbage_collection_rules

        """
        pass

    def test_prepare_garbage_collection_commits(self):
        """Test case for prepare_garbage_collection_commits

        save lists of active and expired commits for garbage collection  # noqa: E501
        """
        pass

    def test_prepare_garbage_collection_uncommitted(self):
        """Test case for prepare_garbage_collection_uncommitted

        save repository uncommitted metadata for garbage collection  # noqa: E501
        """
        pass

    def test_set_garbage_collection_rules(self):
        """Test case for set_garbage_collection_rules

        """
        pass

    def test_set_garbage_collection_rules_preflight(self):
        """Test case for set_garbage_collection_rules_preflight

        """
        pass


if __name__ == '__main__':
    unittest.main()
