from app.ingestion.pipeline import IngestionPipeline


class PDFService:

    def __init__(self):
        self.pipeline = IngestionPipeline()

    def upload_pdf(self, file_path, file_hash=None):
        return self.pipeline.process_pdf(file_path, file_hash=file_hash)
