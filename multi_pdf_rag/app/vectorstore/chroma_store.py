import gc
import shutil
import time
from pathlib import Path

from langchain_chroma import Chroma
from app.core.config import settings
from app.ingestion.embeddings import EmbeddingModel


class ChromaVectorStore:

    def __init__(self):
        self.embedding_model = EmbeddingModel.load_embeddings()
        self.db = None

    def _get_db(self):
        if self.db is None:
            self.db = Chroma(
                persist_directory=settings.CHROMA_DB_DIR,
                embedding_function=self.embedding_model
            )
        return self.db

    def _close_db(self):
        if self.db is None:
            return

        if hasattr(self.db, "_client") and self.db._client is not None:
            try:
                self.db._client.close()
            except Exception:
                pass

        self.db = None
        gc.collect()

    def add_documents(self, documents):
        db = self._get_db()
        ids = [doc.metadata.get("chunk_id") for doc in documents]
        if all(ids):
            db.add_documents(documents, ids=ids)
        else:
            db.add_documents(documents)
        try:
            db.persist()
        except AttributeError:
            pass

    def has_document(self, file_hash=None, source_name=None):
        db = self._get_db()

        if file_hash:
            filters = [{"file_hash": file_hash}]
        elif source_name:
            filters = [{"source": source_name}]
        else:
            filters = []

        for where_filter in filters:
            try:
                result = db.get(where=where_filter, limit=1)
                if result.get("ids"):
                    return True
            except Exception:
                continue

        return False

    def get_stats(self):
        db = self._get_db()
        client = getattr(db, "client", None) or getattr(db, "_client", None)

        collections = None
        counts = {}

        if client is not None:
            try:
                if hasattr(client, "list_collections"):
                    cols = client.list_collections()
                elif hasattr(client, "get_collections"):
                    cols = client.get_collections()
                else:
                    cols = []

                collections = []
                for collection in cols:
                    if hasattr(collection, "name"):
                        collections.append(getattr(collection, "name"))
                    elif isinstance(collection, dict):
                        collections.append(collection.get("name"))
                    else:
                        collections.append(str(collection))
            except Exception:
                collections = None

            if collections:
                for name in collections:
                    try:
                        collection = client.get_collection(name)
                        if hasattr(collection, "count"):
                            counts[name] = collection.count()
                        elif hasattr(collection, "peek"):
                            peek = collection.peek(1000)
                            counts[name] = len(peek.get("ids", []))
                        else:
                            counts[name] = None
                    except Exception as exc:
                        counts[name] = f"error: {exc}"

        persist_path = Path(settings.CHROMA_DB_DIR)
        dirs = []
        if persist_path.exists():
            dirs = [path.name for path in persist_path.iterdir() if path.is_dir()]

        return {
            "collections_reported": collections,
            "counts": counts,
            "persist_path": str(persist_path),
            "collection_dirs": dirs,
        }

    def clear(self):
        self._close_db()

        persist_path = Path(settings.CHROMA_DB_DIR)
        if persist_path.exists():
            for attempt in range(5):
                try:
                    shutil.rmtree(persist_path)
                    break
                except PermissionError:
                    if attempt == 4:
                        raise
                    time.sleep(0.2)

        persist_path.mkdir(parents=True, exist_ok=True)
        self.db = Chroma(
            persist_directory=settings.CHROMA_DB_DIR,
            embedding_function=self.embedding_model
        )

    def similarity_search(self, query, k=5):
        db = self._get_db()
        return db.similarity_search(query, k=k)

    def as_retriever(self):
        db = self._get_db()
        return db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
