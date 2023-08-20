import requests
from typing import List, Iterator, Tuple, Optional
from datetime import datetime
from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
import json
from src.db.models import DataSource
from src.datasource.interface import DataSource as DataSourceInterface, DataSourceUpdate


class DebeziumDataSource(DataSourceInterface):
    def __init__(
        self,
        debezium_url: str,
        kafka_url: str,
        refresh_topics_ms: int = 1000,
    ) -> None:
        self.consumer = KafkaConsumer(
            bootstrap_servers=[kafka_url],
            auto_offset_reset="earliest",
            key_deserializer=lambda x: json.loads(x.decode("utf-8")) if x else None,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")) if x else None,
            consumer_timeout_ms=refresh_topics_ms,
        )
        self.debezium_url = debezium_url

    def add_postgres_connector(
        self,
        id: int,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        table: str,
    ) -> None:
        response = requests.post(
            f"{self.debezium_url}/connectors",
            json={
                "name": f"inquest-{id}",
                "config": {
                    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                    "plugin.name": "pgoutput",
                    "publication.autocreate.mode": "filtered",
                    "include.schema.changes": "false",
                    "database.hostname": host,
                    "database.port": port,
                    "database.user": user,
                    "database.password": password,
                    "database.dbname": database,
                    "table.include.list": table,
                    "topic.prefix": f"inquest.debezium.postgres.{id}",
                },
            },
        )
        response.raise_for_status()

    def add_mongo_connector(self, id: str, url: str, collection: str) -> None:
        response = requests.post(
            f"{self.debezium_url}/connectors",
            json={
                "name": f"inquest-{id}",
                "config": {
                    "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
                    "mongodb.connection.string": url,
                    "collection.include.list": collection,
                    "topic.prefix": f"inquest.debezium.mongo.{id}",
                },
            },
        )
        response.raise_for_status()

    @staticmethod
    def get_postgres_topics() -> List[str]:
        data_sources = DataSource.select().where(DataSource.type == "postgres")
        topics = []
        for source in data_sources:
            config = json.loads(source.config)
            topics.append(f"inquest.debezium.postgres.{source.id}.{config['table']}")
        return topics

    @staticmethod
    def get_mongo_topics() -> List[str]:
        data_sources = DataSource.select().where(DataSource.type == "mongo")
        topics = []
        for source in data_sources:
            config = json.loads(source.config)
            topics.append(f"inquest.debezium.mongo.{source.id}.{config['collection']}")
        return topics

    @staticmethod
    def parse_postgres_message(message: ConsumerRecord) -> DataSourceUpdate:
        data_source = message.topic.split(".")[3]
        document_id = str(message.key["payload"]["id"])

        if message.value["payload"]["op"] == "d":
            document = None
        else:
            document = "\n".join(
                f"{k}: {v}" for k, v in message.value["payload"]["after"].items()
            )

        return {
            "data_source": data_source,
            "document_id": document_id,
            "document": document,
        }

    @staticmethod
    def parse_mongo_message(message: ConsumerRecord) -> DataSourceUpdate:
        data_source = message.topic.split(".")[3]
        document_id = json.loads(message.key["payload"]["id"])["$oid"]

        if message.value["payload"]["op"] == "d":
            document = None
        else:
            after_item = json.loads(message.value["payload"]["after"])
            after_item.pop("_id")
            document = "\n".join(f"{k}: {v}" for k, v in after_item.items())

        return {
            "data_source": data_source,
            "document_id": document_id,
            "document": document,
        }

    def get_topics(self) -> List[str]:
        return [*self.get_postgres_topics(), *self.get_mongo_topics()]

    def listen_for_updates(self) -> Iterator[DataSourceUpdate]:
        past_topics = []

        while True:
            topics = self.get_topics()
            if topics and topics != past_topics:
                self.consumer.subscribe(topics)
                past_topics = topics

            for message in self.consumer:
                if message.value:
                    if message.topic.startswith("inquest.debezium.postgres"):
                        yield self.parse_postgres_message(message)
                    elif message.topic.startswith("inquest.debezium.mongo"):
                        yield self.parse_mongo_message(message)
                    else:
                        raise Exception("Unknown topic")

    def get_documents(
        self, updated_since: Optional[datetime] = None
    ) -> Iterator[Tuple[str, str]]:
        raise NotImplementedError
