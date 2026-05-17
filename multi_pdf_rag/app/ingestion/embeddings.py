from langchain_huggingface import HuggingFaceEmbeddings
from functools import lru_cache

from app.core.config import settings


class EmbeddingModel:

    @staticmethod
    @lru_cache(maxsize=1)
    def load_embeddings():
        return HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
