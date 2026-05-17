from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@router.get("/vec_stats")
def vec_stats():
    from app.vectorstore.chroma_store import ChromaVectorStore

    try:
        return ChromaVectorStore().get_stats()

    except Exception as exc:
        return {"error": str(exc)}
