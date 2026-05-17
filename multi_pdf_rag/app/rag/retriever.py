from app.vectorstore.chroma_store import ChromaVectorStore


class RetrieverManager:

    def __init__(self):
        self.vectorstore = ChromaVectorStore()

    def get_relevant_docs(self, query):
        return self.vectorstore.similarity_search(query)