import re

from app.rag.retriever import RetrieverManager
from app.rag.chains import RAGChain


FALLBACK_TEXT = "I could not find relevant information in the uploaded documents."

STOPWORDS = {
    "about",
    "above",
    "all",
    "also",
    "and",
    "any",
    "are",
    "can",
    "compare",
    "describe",
    "document",
    "documents",
    "does",
    "explain",
    "find",
    "from",
    "give",
    "have",
    "how",
    "important",
    "insight",
    "insights",
    "into",
    "key",
    "list",
    "pdf",
    "pdfs",
    "please",
    "provide",
    "show",
    "summarize",
    "summary",
    "tell",
    "that",
    "the",
    "their",
    "there",
    "these",
    "this",
    "uploaded",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


class ChatService:

    def __init__(self):
        self.retriever = RetrieverManager()
        self.chain = RAGChain()

    def _question_terms(self, question):
        words = re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", question.lower())
        return [word for word in words if len(word) > 2 and word not in STOPWORDS]

    def _has_keyword_support(self, docs, question):
        terms = self._question_terms(question)
        if not terms:
            return True

        combined_context = " ".join(
            (getattr(doc, "page_content", "") or "").lower()
            for doc in docs
        )
        return any(term in combined_context for term in terms)

    def ask_question(self, question):

        docs = self.retriever.get_relevant_docs(question)

        if not docs or not self._has_keyword_support(docs, question):
            return {
                "answer": FALLBACK_TEXT,
                "sources": []
            }

        response = self.chain.generate(docs, question)

        if isinstance(response, str) and response.strip() == FALLBACK_TEXT:
            return {
                "answer": FALLBACK_TEXT,
                "sources": []
            }

        # Default: return the LLM response and the doc sources
        sources = []
        for doc in docs:
            sources.append({
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page")
            })

        return {
            "answer": response,
            "sources": sources
        }
