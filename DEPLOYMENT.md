# Deployment

This project is ready for Docker-based deployment. The public app is Streamlit; FastAPI runs inside the same container on port `8000`.

## Required Environment Variables

Set these in your hosting provider:

```text
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-1.5-flash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Most platforms provide `PORT` automatically. The app uses that for Streamlit.

## Local Docker Run

```powershell
docker build -t multipdf-rag .
docker run --env-file .env -p 8501:8501 multipdf-rag
```

Open:

```text
http://localhost:8501
```

## Platform Settings

Use these settings on Render, Railway, Fly.io, or any Docker host:

```text
Build: docker build -t multipdf-rag .
Start: python -m multi_pdf_rag.app.run
Public port: $PORT
```

For Docker platforms, you usually only need to point the service at this repository and set the environment variables above.

## Notes

- Uploaded PDFs and Chroma vector data are generated at runtime and ignored by git.
- If your host has ephemeral storage, uploaded documents and embeddings reset whenever the container restarts.
- For persistent production use, attach a persistent disk and set:

```text
UPLOAD_DIR=/path/to/persistent/raw
CHROMA_DB_DIR=/path/to/persistent/vectordb
```
