from typing import Any, ClassVar, List, Optional, Self, Type

import bson
import pymongo
import pymongo.errors
import pymongo.results
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from pymongo.collection import Collection
from pymongo.database import Database

from pydantic_mongo_document.encoder import JsonEncoder
from pydantic_mongo_document.exceptions import DocumentNotFound


class Document(BaseModel):
    __primary_key__: ClassVar[str] = "id"

    __database__: ClassVar[str]
    __collection__: ClassVar[str]
    __mongo_uri__: ClassVar[str]

    NotFoundError: ClassVar[Type[Exception]] = DocumentNotFound
    DuplicateKeyError: ClassVar[Type[Exception]] = pymongo.errors.DuplicateKeyError

    encoder: ClassVar[JsonEncoder] = JsonEncoder()

    id: str = Field(default_factory=lambda: str(bson.ObjectId()), alias="_id")

    @property
    def primary_key(self) -> Any:
        return getattr(self, self.__primary_key__)

    @property
    def primary_key_field_name(self) -> str:
        return self.model_fields[self.__primary_key__].alias or self.__primary_key__

    @classmethod
    def set_mongo_uri(cls, mongo_uri: str) -> None:
        cls.__mongo_uri__ = mongo_uri

    @classmethod
    def client(cls) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(cls.__mongo_uri__)

    @classmethod
    def sync_client(cls) -> pymongo.MongoClient[Any]:
        return pymongo.MongoClient(cls.__mongo_uri__)

    @classmethod
    def database(cls) -> AsyncIOMotorDatabase:
        return cls.client()[cls.__database__]

    @classmethod
    def sync_database(cls) -> Database[Any]:
        return cls.sync_client()[cls.__database__]

    @classmethod
    def collection(cls) -> AsyncIOMotorCollection:
        return cls.database()[cls.__collection__]

    @classmethod
    def sync_collection(cls) -> Collection[Any]:
        return cls.sync_database()[cls.__collection__]

    @classmethod
    async def create_indexes(cls) -> None:
        """Creates indexes for collection."""

    @classmethod
    async def one(
        cls,
        document_id: str | None = None,
        add_query: dict[str, Any] | None = None,
        required: bool = True,
        **kwargs: Any,
    ) -> Optional[Self]:
        """Finds one document by ID."""

        query = {}
        if document_id is not None:
            query["_id"] = document_id
        if add_query is not None:
            query.update(add_query)

        query = cls.encoder.encode_dict(query, reveal_secrets=True)

        result = await cls.collection().find_one(query, **kwargs)

        if result is not None:
            return cls(**result)

        if required:
            raise cls.NotFoundError()

        return None

    @classmethod
    async def all(
        cls,
        document_ids: List[str | bson.ObjectId] | None = None,
        add_query: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> List[Self]:
        """Finds all documents based in IDs."""

        query = {}
        if document_ids is not None:
            query["_id"] = {"$in": document_ids}
        if add_query is not None:
            query.update(add_query)

        documents = []

        query = cls.encoder.encode_dict(query, reveal_secrets=True)

        cursor = cls.collection().find(query, **kwargs)
        async for document in cursor:
            documents.append(cls(**document))

        return documents

    @classmethod
    async def count(cls, add_query: Optional[dict[str, Any]] = None, **kwargs: Any) -> int:
        """Counts documents in collection."""

        query = {}
        if add_query is not None:
            query.update(add_query)

        query = cls.encoder.encode_dict(query, reveal_secrets=True)

        return await cls.collection().count_documents(query, **kwargs)

    async def delete(self) -> pymongo.results.DeleteResult:
        """Deletes document from collection."""

        query = self.encoder.encode_dict(
            {self.primary_key_field_name: self.primary_key},
        )

        return await self.collection().delete_one(query)

    async def commit_changes(self, fields: Optional[List[str]] = None) -> None:
        """Saves changed document to collection."""

        search_query: dict[str, Any] = {self.primary_key_field_name: self.primary_key}
        update_query: dict[str, Any] = {"$set": {}}

        if not fields:
            fields = [field for field in self.model_fields.keys() if field != self.__primary_key__]

        data = self.encoder.encode_dict(self.model_dump(), reveal_secrets=True)

        for field in fields:
            update_query["$set"].update({field: data[field]})

        await self.collection().update_one(search_query, update_query)

    async def insert(self) -> Self:
        """Inserts document into collection."""

        obj = await self.collection().insert_one(
            self.encoder.encode_dict(
                self.model_dump(by_alias=True),
                reveal_secrets=True,
            )
        )

        if getattr(self, self.__primary_key__, None) is None:
            setattr(self, self.__primary_key__, obj.inserted_id)

        return self
