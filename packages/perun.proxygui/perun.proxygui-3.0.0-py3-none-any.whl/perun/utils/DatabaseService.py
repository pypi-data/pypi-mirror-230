from pymongo import MongoClient
from pymongo.collection import Collection


class DatabaseService:
    def __init__(self, cfg):
        self.__CFG = cfg

    def get_mongo_db_collection(self, cfg_db_name: str) -> Collection:
        client = MongoClient(self.__CFG[cfg_db_name]["connection_string"])
        database_name = self.__CFG[cfg_db_name]["database_name"]
        collection_name = self.__CFG[cfg_db_name]["collection_name"]

        return client[database_name][collection_name]
