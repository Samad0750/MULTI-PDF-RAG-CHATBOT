from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.rag.prompt import SYSTEM_PROMPT


class RAGChain:

    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "Context:\n{context}\n\nQuestion:\n{input}")
        ])

        self.chain = create_stuff_documents_chain(
            self.llm,
            self.prompt
        )

    def generate(self, docs, question):
        if not docs:
            return "I could not find relevant information in the uploaded documents."

        return self.chain.invoke({
            "context": docs,
            "input": question
        })
