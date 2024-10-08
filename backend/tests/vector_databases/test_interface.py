from turbine.vector_databases import VectorDocument
from .utils import create_embedding, metadata, create_instance
import pytest


@pytest.mark.parametrize(
    "type",
    [
        "pinecone",
        "milvus",
    ],
)
class TestVectorDatabase:
    def test_init(self, type: str):
        db = create_instance(type)
        assert db is not None

    def test_validate_config(self, type: str):
        db = create_instance(type)
        db.validate_config()

    def test_insert(self, type: str):
        db = create_instance(type)
        db.insert(
            [
                VectorDocument(
                    id="test-id-1",
                    embedding=create_embedding(),
                    metadata=metadata,
                    content="test-content-1",
                ),
                VectorDocument(
                    id="test-id-2",
                    embedding=create_embedding(),
                    metadata=metadata,
                    content="test-content-2",
                ),
            ]
        )

    def test_embedding_dimension(self, type: str):
        db = create_instance(type)
        assert db.embedding_dimension == 1536
