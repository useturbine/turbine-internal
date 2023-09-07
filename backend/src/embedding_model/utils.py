from src.schema import EmbeddingModel as EmbeddingModelName, SimilarityMetric
from .interface import EmbeddingModel
from .hugging_face import HuggingFaceModel
from .openai import OpenAIModel
from config import Config
from pydantic import BaseModel


class EmbeddingModelItem(BaseModel):
    model: EmbeddingModel
    dimensions: int
    similarity_metric: SimilarityMetric

    class Config:
        arbitrary_types_allowed = True


def get_embedding_model(name: EmbeddingModelName) -> EmbeddingModelItem:
    if name == "all-MiniLM-L6-v2":
        return EmbeddingModelItem(
            model=HuggingFaceModel(
                token=Config.huggingface_token,
                model="sentence-transformers/all-MiniLM-L6-v2",
            ),
            dimensions=384,
            similarity_metric="cosine",
        )
    elif name == "text-embedding-ada-002":
        return EmbeddingModelItem(
            model=OpenAIModel(
                api_key=Config.openai_token, model="text-embedding-ada-002"
            ),
            dimensions=1536,
            similarity_metric="cosine",
        )
    raise ValueError("Invalid embedding model")
