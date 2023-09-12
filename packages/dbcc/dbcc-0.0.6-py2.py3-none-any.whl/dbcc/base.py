from typing import Any


class TableEngine:
    collection_name: str = None
    db_name: str = None
    url: str = None

    def __init__(self, url: str, db_name: str, collection_name: str = None):
        self.url = url
        self.db_name = db_name
        self.collection_name = collection_name

    def __getitem__(self, key):
        return TableEngine(self.url, self.db_name, key)

    async def find_batch(
        self,
        pattern: dict = None,
        skip: int = None,
        limit: int = None,
        sort: list = None,
        projection: dict = None,
    ) -> list:
        raise NotImplementedError()

    async def find_batch_raw(
        self,
        pattern: dict = None,
        skip: int = None,
        limit: int = None,
        sort: list = None,
        projection: dict = None,
    ) -> list:
        raise NotImplementedError()

    async def create(self, entry: dict) -> dict:
        raise NotImplementedError()

    async def update_by_id(self, id: Any, payload: dict):
        raise NotImplementedError()

    async def delete_by_id(self, id: Any):
        raise NotImplementedError()

    async def find_single(self, field: str, value):
        raise NotImplementedError()
