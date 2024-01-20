import pymongo
from typing import Union, List, Dict, Any
from core.settings import MongoSettings


class MongoManager:
    def __init__(self):
        settings = MongoSettings()
        self.client = pymongo.MongoClient(f"mongodb://{settings.mongo_host}:{settings.mongo_port}/")
        self.db = self.client["api-service"]
        self.data = self.db["data"]

    def insert_one(self, d: Dict) -> None:
        self.data.insert_one(d).inserted_id

    def find_one(self, name: str) -> Union[Any, None]:
        return self.data.find_one({"name": name})

    def find_data(self, query: str) -> List[Union[Any, None]]:
        return [d for d in self.data.find(dict((query.split("="),)))]

    def find_all_data(self) -> List[Union[Any, None]]:
        return [doc for doc in self.data.find()]

    def replace_one(self, name: str, d: Dict) -> None:
        self.data.replace_one({"name": name}, d)

    def delete_one(self, name: str) -> None:
        self.data.delete_one({"name": name})
