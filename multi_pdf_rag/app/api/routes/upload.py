from fastapi import APIRouter, UploadFile, File, Header, HTTPException
import hashlib
import os
from pathlib import Path

from app.services.pdf_service import PDFService
from app.core.config import settings

router = APIRouter()

pdf_service = PDFService()

UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    reset_vector_store: bool = Header(False, alias="X-Reset-Vector-Store")
):

    try:
        if reset_vector_store:
            pdf_service.pipeline.vectorstore.clear()

        safe_filename = Path(file.filename or "uploaded.pdf").name
        if not safe_filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        file_hash = hashlib.sha256()

        with open(file_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                file_hash.update(chunk)
                buffer.write(chunk)

        result = pdf_service.upload_pdf(file_path, file_hash=file_hash.hexdigest())

        try:
            vec_stats = pdf_service.pipeline.vectorstore.get_stats()
        except Exception as exc:
            vec_stats = {"error": str(exc)}

        return {"upload_result": result, "vec_stats": vec_stats}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
