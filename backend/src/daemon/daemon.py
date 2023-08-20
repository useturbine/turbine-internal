from src.embedding_model.interface import EmbeddingModel
from src.vectordb.milvus import MilvusVectorDB
from src.datasource.debezium import Debezium


class Daemon:
    def __init__(
        self,
        debezium: Debezium,
        embedding_model: EmbeddingModel,
        vector_db: MilvusVectorDB,
    ) -> None:
        self.debezium = debezium
        self.model = embedding_model
        self.vector_db = vector_db

    def run(self):
        for update in self.debezium.listen_for_updates():
            collection_name = f"inquest_{update['data_source']}"

            if update["document"]:
                print(f"Adding {update['document_id']} to {collection_name}")
                embedding = self.model.get_embedding(update["document"])
                self.vector_db.insert(
                    collection_name,
                    [[update["document_id"]], [embedding]],
                )
            else:
                print(f"Deleting {update['document_id']} from {collection_name}")
                self.vector_db.delete(
                    collection_name,
                    update["document_id"],
                )
