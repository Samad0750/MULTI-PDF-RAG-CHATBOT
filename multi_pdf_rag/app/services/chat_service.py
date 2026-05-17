from app.rag.retriever import RetrieverManager
from app.rag.chains import RAGChain


class ChatService:

    def __init__(self):
        self.retriever = RetrieverManager()
        self.chain = RAGChain()

    def ask_question(self, question):

        docs = self.retriever.get_relevant_docs(question)

        response = self.chain.generate(docs, question)
        # If the chain returned the strict 'not found' message, attempt a
        # lightweight keyword-based extraction from the retrieved chunks as a
        # fallback. This helps with short definitional queries that are present
        # verbatim in the documents but where the LLM conservatively declined.
        fallback_text = "I could not find relevant information in the uploaded documents."

        if isinstance(response, str) and response.strip() == fallback_text:
            q_terms = [t.lower() for t in question.split() if len(t) > 2]
            matches = []
            for doc in docs:
                content = (getattr(doc, "page_content", "") or "").lower()
                if any(term in content for term in q_terms):
                    # take a short excerpt around the first occurrence
                    for term in q_terms:
                        idx = content.find(term)
                        if idx != -1:
                            start = max(0, idx - 120)
                            end = min(len(content), idx + 400)
                            excerpt = doc.page_content[start:end]
                            matches.append((excerpt.strip(), doc))
                            break

            if matches:
                # build a concise, context-grounded answer from matches
                answer_parts = []
                sources = []
                used = set()
                for excerpt, doc in matches[:3]:
                    key = (doc.metadata.get("source"), doc.metadata.get("page"))
                    if key in used:
                        continue
                    used.add(key)
                    answer_parts.append(excerpt.replace("\n", " ")[:800])
                    sources.append({
                        "source": doc.metadata.get("source"),
                        "page": doc.metadata.get("page")
                    })

                answer = "\n\n".join(answer_parts)

                return {
                    "answer": answer,
                    "sources": sources,
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