from pathlib import Path

from app.ingestion.loader import PDFLoader
from app.ingestion.splitter import DocumentSplitter
from app.ingestion.metadata import MetadataManager
from app.vectorstore.chroma_store import ChromaVectorStore


class IngestionPipeline:

    def __init__(self):
        self.vectorstore = ChromaVectorStore()

    def process_pdf(self, pdf_path: str, file_hash: str | None = None):
        source_name = Path(pdf_path).name

        if self.vectorstore.has_document(file_hash=file_hash, source_name=source_name):
            return {
                "status": "skipped",
                "reason": "document already indexed",
                "chunks": 0
            }

        documents = PDFLoader.load_pdf(pdf_path)

        chunks = DocumentSplitter.split_documents(documents)

        enriched_chunks = MetadataManager.enrich(
            chunks,
            source_name=source_name,
            file_hash=file_hash
        )

        self.vectorstore.add_documents(enriched_chunks)

        return {
            "status": "success",
            "chunks": len(enriched_chunks)
        }
