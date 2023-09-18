import atexit
import os
import yaml

import pymongo
import redis

from rich.console import Console

from .crypto import Crypto

class Cache:
    """
    # Discord Cache
    A better way to boost youre discord bot performace.

    :copyright: (c) 2023 - present ryzmae
    :license: MIT, see LICENSE for more details.
    """
    def __init__(
        self,
        mongo_uri: str,
        redis_uri: str,
        mongo_db: str = "discord-cache",
        mongo_collection: str = "discord-cache",
    ) -> None:
        
        self.mongo_uri = mongo_uri
        self.redis_uri = redis_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

        self._console = Console()

        self._mongo_client = pymongo.MongoClient(self.mongo_uri)
        self._redis_client = redis.Redis.from_url(self.redis_uri)

        self._crypto = Crypto()

        if "discord-cache.config.yaml" in os.listdir():
            with open("discord-cache.config.yaml", "r") as file:
                config = yaml.safe_load(file)

            self.mongo_uri = config["mongo_uri"]
            self.redis_uri = config["redis_uri"]
            self.mongo_db = config["mongo_db"]
            self.mongo_collection = config["mongo_collection"]

            self._mongo_client = pymongo.MongoClient(mongo_uri)
            self._redis_client = redis.Redis.from_url(redis_uri)

    @atexit.register
    async def insert(self, key: str, value: str) -> None:
        """
        Insert a key and value into the database.

        :param key: The key to insert into the database.
        :param value: The value to insert into the database.
        """
        if self._redis_client.exists(key):
            return

        if self._mongo_client[self.mongo_db][self.mongo_collection].find_one({"key": key}):
            return
        
        self._redis_client.set(key, value)
        self._mongo_client[self.mongo_db][self.mongo_collection].insert_one({"key": key, "value": value})

    @atexit.register
    async def delete(self, key: str) -> None:
        """
        Delete a key from the database.

        :param key: The key to delete from the database.
        """
        if not self._redis_client.exists(key):
            return

        if not self._mongo_client[self.mongo_db][self.mongo_collection].find_one({"key": key}):
            return

        self._redis_client.delete(key)
        self._mongo_client[self.mongo_db][self.mongo_collection].delete_one({"key": key})

    @atexit.register
    async def get(self, key: str) -> str:
        """
        Get a key from the database.

        :param key: The key to get from the database.
        """
        if not self._redis_client.exists(key):
            return

        if not self._mongo_client[self.mongo_db][self.mongo_collection].find_one({"key": key}):
            return

        return self._redis_client.get(key)
    
    @atexit.register
    async def update(self, key: str, value: str) -> None:
        """
        Update a key in the database.

        :param key: The key to update in the database.
        :param value: The value to update in the database.
        """
        if not self._redis_client.exists(key):
            return

        if not self._mongo_client[self.mongo_db][self.mongo_collection].find_one({"key": key}):
            return

        self._redis_client.set(key, value)
        self._mongo_client[self.mongo_db][self.mongo_collection].update_one({"key": key}, {"$set": {"value": value}})

    @atexit.register
    async def clear(self) -> None:
        """
        Clear the database.
        """
        self._redis_client.flushall()
        self._mongo_client[self.mongo_db][self.mongo_collection].drop()
    
    @atexit.register
    async def count(self) -> int:
        """
        Get the amount of keys in the database.
        """
        return len(self._redis_client.keys())
    
    def mongo_required(self, func):
        """
        A decorator to check if the mongo database is connected.
        """
        def wrapper(*args, **kwargs):
            if not self._mongo_client:
                self._console.print("[red]Mongo database not connected.[/red]")
                return

            return func(*args, **kwargs)
        return wrapper
    
    def redis_required(self, func):
        """
        A decorator to check if the redis database is connected.
        """
        def wrapper(*args, **kwargs):
            if not self._redis_client:
                self._console.print("[red]Redis database not connected.[/red]")
                return
            return func(*args, **kwargs)
        return wrapper
    
