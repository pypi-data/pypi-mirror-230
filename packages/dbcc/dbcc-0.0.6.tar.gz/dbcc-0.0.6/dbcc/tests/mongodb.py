import unittest

from dbcc import MongoTableEngine


class TestMongoTableEngine(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        url = "mongodb://localhost:27017"
        db_name = "test"
        self.db = MongoTableEngine(url, db_name, mock_db_in_mem=True)
        self.collection = self.db["test_collection"]

    def test_getitem(self):
        self.collection = self.db["some_collection"]
        self.assertEqual(self.collection.collection_name, "some_collection")

    async def test_create(self):
        test_dict = {"key": "value", "field": "content"}
        saved_dict = await self.collection.create(test_dict)
        self.assertIsNotNone(saved_dict["_id"])
        found_dict = await self.collection.find_single("_id", saved_dict["_id"])
        self.assertIsNotNone(found_dict)
        for k, v in test_dict.items():
            self.assertEqual(found_dict[k], v)
