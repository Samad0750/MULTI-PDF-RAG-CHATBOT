from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentSplitter:

    @staticmethod
    def split_documents(documents):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " "]
        )

        return splitter.split_documents(documents)