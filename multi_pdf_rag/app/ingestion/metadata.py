import uuid


class MetadataManager:

    @staticmethod
    def enrich(documents, source_name, file_hash=None):
        enriched_docs = []

        for idx, doc in enumerate(documents):
            doc.metadata["source"] = source_name
            doc.metadata["chunk_id"] = (
                f"{file_hash}:{idx}" if file_hash else str(uuid.uuid4())
            )
            doc.metadata["chunk_index"] = idx
            if file_hash:
                doc.metadata["file_hash"] = file_hash

            enriched_docs.append(doc)

        return enriched_docs
