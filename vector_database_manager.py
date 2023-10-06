from typing import Optional, Collection

import chromadb

from passage_emebeddinng_object import PassageEmbeddingObject
from chromadb import Documents, EmbeddingFunction, Embeddings, CollectionMetadata
from sklearn.feature_extraction.text import TfidfVectorizer


# TODO: Finetune BERT model for senate documents
class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, texts: Documents) -> Embeddings:
        # embed the documents somehow
        return None


class ChromaClient:
    def __init__(self, path_directory):
        self.chroma_client = chromadb.PersistentClient(path=path_directory)

    # def create_collection(self, collection_name):
    #     return self.chroma_client.create_collection(collection_name)

    def store_documents(self, collection_name, passages: PassageEmbeddingObject):
        collection = self.chroma_client.get_collection(collection_name)
        collection.add(
            documents=passages.passage_embedding,
            metadatas=passages.metadata,
            ids=passages.passage_id,
        )

    @staticmethod
    def build_list_of_properties(properties):
        pass
