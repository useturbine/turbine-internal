from ..embedding_models.interface import EmbeddingModel
from ..embedding_models.hugging_face import HuggingFace
from ..embedding_models.openai import OpenAI
from turbine.config import Config
from pydantic import BaseModel
from typing import Literal

EmbeddingModelName = Literal["text-embedding-ada-002", "all-MiniLM-L6-v2"]
SimilarityMetric = Literal["cosine", "euclidean"]


class EmbeddingModelItem(BaseModel):
    model: EmbeddingModel
    dimensions: int
    similarity_metric: SimilarityMetric

    class Config:
        arbitrary_types_allowed = True


def get_embedding_model(name: EmbeddingModelName) -> EmbeddingModelItem:
    if name == "all-MiniLM-L6-v2":
        return EmbeddingModelItem(
            model=HuggingFace(
                token=Config.huggingface_token,
                model="sentence-transformers/all-MiniLM-L6-v2",
            ),
            dimensions=384,
            similarity_metric="cosine",
        )
    elif name == "text-embedding-ada-002":
        return EmbeddingModelItem(
            model=OpenAI(api_key=Config.openai_token, model="text-embedding-ada-002"),
            dimensions=1536,
            similarity_metric="cosine",
        )
    raise ValueError("Invalid embedding model")
